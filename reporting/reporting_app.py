from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import os
import psycopg2
from datetime import datetime, time
from typing import Optional, List

DATABASE_URL = os.getenv('DATABASE_URL', 'postgres://analytics:analytics@localhost:5432/analytics')

app = FastAPI(title='analytics-reporting')

class PathStat(BaseModel):
    path: str
    views: int

class StatsResponse(BaseModel):
    site_id: str
    date: Optional[str]
    total_views: int
    unique_users: int
    top_paths: List[PathStat]

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.get('/stats', response_model=StatsResponse)
def get_stats(site_id: str = Query(...), date: Optional[str] = Query(None)):
    params = [site_id]
    date_clause = ''
    date_str = None
    if date:
        try:
            dt = datetime.strptime(date, '%Y-%m-%d').date()
            start = datetime.combine(dt, time.min)
            end = datetime.combine(dt, time.max)
            date_clause = 'AND occurred_at >= %s AND occurred_at <= %s'
            params.append(start)
            params.append(end)
            date_str = dt.isoformat()
        except Exception:
            raise HTTPException(status_code=400, detail='date must be YYYY-MM-DD')

    conn = get_conn()
    cur = conn.cursor()

    q_total = f"SELECT COUNT(*) FROM events WHERE site_id = %s {date_clause}"
    cur.execute(q_total, tuple(params))
    total_views = cur.fetchone()[0] or 0

    q_unique = f"SELECT COUNT(DISTINCT user_id) FROM events WHERE site_id = %s {date_clause}"
    cur.execute(q_unique, tuple(params))
    unique_users = cur.fetchone()[0] or 0

    q_paths = f"SELECT path, COUNT(*) AS views FROM events WHERE site_id = %s {date_clause} GROUP BY path ORDER BY views DESC LIMIT 10"
    cur.execute(q_paths, tuple(params))
    rows = cur.fetchall()
    top_paths = []
    for path, views in rows:
        top_paths.append({ 'path': path or '/', 'views': views })

    cur.close()
    conn.close()

    return {
        'site_id': site_id,
        'date': date_str,
        'total_views': int(total_views),
        'unique_users': int(unique_users),
        'top_paths': top_paths
    }
