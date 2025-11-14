from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os, json
import redis.asyncio as aioredis
from typing import Optional
from datetime import datetime

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
REDIS_QUEUE = 'events_queue'

app = FastAPI(title="analytics-ingestion")

class Event(BaseModel):
    site_id: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)
    path: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: str

@app.on_event("startup")
async def startup():
    app.state.redis = aioredis.from_url(REDIS_URL, decode_responses=True)

@app.on_event("shutdown")
async def shutdown():
    try:
        await app.state.redis.close()
    except Exception:
        pass

@app.post('/event', status_code=202)
async def post_event(event: Event):
    try:
        occurred_at = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
    except Exception:
        raise HTTPException(status_code=400, detail='timestamp must be ISO8601')

    payload = {
        'site_id': event.site_id,
        'event_type': event.event_type,
        'path': event.path,
        'user_id': event.user_id,
        'timestamp': occurred_at.isoformat()
    }

    try:
        # push quickly to Redis list
        await app.state.redis.rpush(REDIS_QUEUE, json.dumps(payload))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'queue error: {e}')

    return {"status": "accepted"}
