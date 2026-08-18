-- Upgrade an already-created local development environment.
-- This is a psql script because it switches databases with \connect.
-- Run:
-- psql -U postgres -d postgres -f database\03_upgrade_existing.sql

\connect supplier_db

CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE supplier_onboarding_workflow
    ADD COLUMN IF NOT EXISTS correlation_id UUID;

UPDATE supplier_onboarding_workflow
SET correlation_id = gen_random_uuid()
WHERE correlation_id IS NULL;

ALTER TABLE supplier_onboarding_workflow
    ALTER COLUMN correlation_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS ix_supplier_onboarding_correlation_id
    ON supplier_onboarding_workflow (correlation_id);

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

ALTER TABLE outbox_messages
    ADD COLUMN IF NOT EXISTS attempts INTEGER;

UPDATE outbox_messages
SET attempts = 0
WHERE attempts IS NULL;

ALTER TABLE outbox_messages
    ALTER COLUMN attempts SET DEFAULT 0;

ALTER TABLE outbox_messages
    ALTER COLUMN attempts SET NOT NULL;

-- Correct the Supplier status constraint from older bootstrap scripts.
ALTER TABLE suppliers
    DROP CONSTRAINT IF EXISTS ck_suppliers_status;

UPDATE suppliers
SET status = UPPER(status)
WHERE status IN (
    'draft',
    'under_review',
    'approved',
    'rejected'
);

ALTER TABLE suppliers
    ADD CONSTRAINT ck_suppliers_status
    CHECK (
        status IN (
            'DRAFT',
            'UNDER_REVIEW',
            'APPROVED',
            'REJECTED'
        )
    );

\connect sap_integration_db

CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE sap_sync_operations
    ADD COLUMN IF NOT EXISTS correlation_id UUID;

UPDATE sap_sync_operations
SET correlation_id = gen_random_uuid()
WHERE correlation_id IS NULL;

ALTER TABLE sap_sync_operations
    ALTER COLUMN correlation_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS ix_sap_sync_operations_correlation_id
    ON sap_sync_operations (correlation_id);

ALTER TABLE outbox_messages
    ADD COLUMN IF NOT EXISTS attempts INTEGER;

UPDATE outbox_messages
SET attempts = 0
WHERE attempts IS NULL;

ALTER TABLE outbox_messages
    ALTER COLUMN attempts SET DEFAULT 0;

ALTER TABLE outbox_messages
    ALTER COLUMN attempts SET NOT NULL;
