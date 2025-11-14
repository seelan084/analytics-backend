# Analytics Backend (Docker)

Start:
  docker-compose up --build

Ingest example:
  curl -X POST "http://localhost:8000/event" -H "Content-Type: application/json" -d '{
    "site_id": "site-abc-123",
    "event_type": "page_view",
    "path": "/pricing",
    "user_id": "user-xyz-789",
    "timestamp": "2025-11-12T19:30:01Z"
  }'

Query stats:
  curl "http://localhost:8001/stats?site_id=site-abc-123&date=2025-11-12"
