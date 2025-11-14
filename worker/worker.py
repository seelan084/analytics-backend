import os, time, json
import redis
import psycopg2
from datetime import datetime, timezone, timedelta

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgres://analytics:analytics@localhost:5432/analytics')
QUEUE = 'events_queue'

print('🔧 worker starting...')

r = redis.from_url(REDIS_URL, decode_responses=True)

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def insert_event(conn, obj):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO events (site_id, event_type, path, user_id, occurred_at)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (obj.get('site_id'), obj.get('event_type'), obj.get('path'), obj.get('user_id'), obj.get('occurred_at'))
    )
    conn.commit()
    cur.close()

def process_payload(raw):
    try:
        obj = json.loads(raw)
    except Exception as e:
        print('invalid json in queue', e)
        return

    # basic validation
    if 'site_id' not in obj or 'event_type' not in obj or 'timestamp' not in obj:
        print('missing required fields, dropping', obj)
        return

    # parse timestamp
    try:
        occurred_at = datetime.fromisoformat(obj['timestamp'])
    except Exception:
        try:
            occurred_at = datetime.strptime(obj['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
        except Exception as e:
            print('bad timestamp', obj.get('timestamp'), e)
            return

    # Attach occurred_at in ISO for DB (psycopg2 will accept datetime object too)
    obj['occurred_at'] = occurred_at

    # Insert into DB
    for attempt in range(3):
        try:
            conn = get_conn()
            insert_event(conn, obj)
            conn.close()
            return
        except Exception as e:
            print('db insert failed attempt', attempt+1, e)
            time.sleep(1)
    print('failed to insert after retries, dropping:', obj)

# Main loop: BRPOP blocking
while True:
    try:
        item = r.brpop(QUEUE, timeout=5)
        if item is None:
            continue
        _, raw = item
        process_payload(raw)
    except Exception as e:
        print('worker error', e)
        time.sleep(1)
