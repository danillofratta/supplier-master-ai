-- Run against supplier_db.

CREATE TABLE IF NOT EXISTS inbox_messages (
    message_id UUID PRIMARY KEY,
    event_type VARCHAR(200) NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE inbox_messages
    ADD COLUMN IF NOT EXISTS processed_at TIMESTAMPTZ;

UPDATE inbox_messages
SET processed_at = NOW()
WHERE processed_at IS NULL;

ALTER TABLE inbox_messages
    ALTER COLUMN processed_at SET DEFAULT NOW();

ALTER TABLE inbox_messages
    ALTER COLUMN processed_at SET NOT NULL;

CREATE INDEX IF NOT EXISTS ix_supplier_inbox_event_type
    ON inbox_messages (event_type);

CREATE INDEX IF NOT EXISTS ix_supplier_inbox_processed_at
    ON inbox_messages (processed_at);
