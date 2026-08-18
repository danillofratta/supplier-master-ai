-- Run against sap_integration_db.
-- Aligns the physical table with consumer-sap and worker-sap-outbox.

ALTER TABLE outbox_messages
ADD COLUMN IF NOT EXISTS attempts INTEGER;

UPDATE outbox_messages
SET attempts = 0
WHERE attempts IS NULL;

ALTER TABLE outbox_messages
ALTER COLUMN attempts SET DEFAULT 0;

ALTER TABLE outbox_messages
ALTER COLUMN attempts SET NOT NULL;

CREATE INDEX IF NOT EXISTS ix_sap_outbox_pending
    ON outbox_messages (created_at)
    WHERE processed_at IS NULL;

SELECT
    message_id,
    event_type,
    attempts,
    processed_at,
    created_at
FROM outbox_messages
ORDER BY created_at DESC;
