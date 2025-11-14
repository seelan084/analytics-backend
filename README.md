# Analytics Backend

## Overview

This project implements a backend service for capturing website analytics events.  
It consists of three main components:

1. **Ingestion API**: Fast endpoint to receive events and push them to a queue.  
2. **Worker/Processor**: Background worker that consumes events from the queue and writes them to the database.  
3. **Reporting API**: Reads aggregated data from the database and provides summarized statistics.

---

## Architecture Decisions

- **Asynchronous Processing**:  
  The ingestion API does not write directly to the database. Instead, it pushes incoming events to a Redis queue.  
  A background worker consumes events from the queue and writes them to PostgreSQL.  
  This ensures that the ingestion endpoint is extremely fast and can handle high volumes of requests.

- **Technology Stack**:
  - **Python + FastAPI**: For both ingestion and reporting APIs.
  - **Redis**: Queue for asynchronous event processing.
  - **PostgreSQL**: Persistent storage of events.
  - **Docker & Docker Compose**: Containerized deployment of all services.

---

## Database Schema

**Table: `events`**

| Column       | Type                | Description                      |
| ------------ | ----------------- | -------------------------------- |
| id           | SERIAL PRIMARY KEY | Unique identifier of the event   |
| site_id      | TEXT               | Identifier for the site          |
| event_type   | TEXT               | Type of event (e.g., page_view) |
| path         | TEXT               | URL path of the event            |
| user_id      | TEXT               | Identifier for the user          |
| occurred_at  | TIMESTAMPTZ        | Time the event occurred          |
| created_at   | TIMESTAMPTZ        | Time the event was saved         |

**Indexes**:  
- `CREATE INDEX idx_site_id ON events(site_id);`  
- `CREATE INDEX idx_occurred_at ON events(occurred_at);`  

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/seelan084/analytics-backend.git
cd analytics-backend
---

2. **Build and start services**

```bash
docker-compose up --build


3. **Verify services

Ingestion API: http://localhost:8000

Reporting API: http://localhost:8001

Redis: Default port 6379

PostgreSQL: Default port 5432

API Usage:
Ingestion API

Endpoint: POST /event
Body (JSON):

{
  "site_id": "site-abc-123",
  "event_type": "page_view",
  "path": "/pricing",
  "user_id": "user-xyz-789",
  "timestamp": "2025-11-12T19:30:01Z"
}


Example:

curl -X POST "http://localhost:8000/event" \
-H "Content-Type: application/json" \
-d '{
  "site_id": "site-abc-123",
  "event_type": "page_view",
  "path": "/pricing",
  "user_id": "user-xyz-789",
  "timestamp": "2025-11-12T19:30:01Z"
}'


Response:

{"status": "accepted"}

Reporting API

Endpoint: GET /stats
Query Parameters:

site_id (required)

date (optional, format: YYYY-MM-DD)

Example:

curl "http://localhost:8001/stats?site_id=site-abc-123&date=2025-11-12"


Response:

{
  "site_id": "site-abc-123",
  "date": "2025-11-12",
  "total_views": 1450,
  "unique_users": 212,
  "top_paths": [
    { "path": "/pricing", "views": 700 },
    { "path": "/blog/post-1", "views": 500 },
    { "path": "/", "views": 250 }
  ]
}

