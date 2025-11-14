CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    site_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    path TEXT,
    user_id TEXT,
    occurred_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_events_site_date ON events(site_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_events_site_path ON events(site_id, path);
