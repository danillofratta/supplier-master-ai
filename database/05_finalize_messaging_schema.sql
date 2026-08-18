-- Run the SAP section against sap_integration_db and the Supplier section
-- against supplier_db, as indicated below.

-- =========================================================
-- sap_integration_db
-- =========================================================
-- psql -U postgres -d sap_integration_db -f database/05_finalize_messaging_schema.sql
-- The guarded statements below are safe when rerun.

ALTER TABLE IF EXISTS outbox_messages
    ADD COLUMN IF NOT EXISTS attempts INTEGER;

UPDATE outbox_messages
SET attempts = 0
WHERE attempts IS NULL;

ALTER TABLE IF EXISTS outbox_messages
    ALTER COLUMN attempts SET DEFAULT 0;

ALTER TABLE IF EXISTS outbox_messages
    ALTER COLUMN attempts SET NOT NULL;

CREATE INDEX IF NOT EXISTS ix_sap_outbox_pending
    ON outbox_messages (created_at)
    WHERE processed_at IS NULL;
