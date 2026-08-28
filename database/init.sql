-- Supplier Master AI - consolidated PostgreSQL bootstrap/alignment script.
--
-- Intended uses:
--   1) Docker postgres initialization through /docker-entrypoint-initdb.d
--   2) Local/manual schema alignment:
--        psql -U postgres -d postgres -f database/init.sql
--
-- This is a psql script (uses \connect and \gexec).
-- Production deployments should use controlled migrations instead of bootstrap DDL.

\connect postgres

SELECT 'CREATE DATABASE supplier_db'
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = 'supplier_db'
)\gexec

SELECT 'CREATE DATABASE sap_integration_db'
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = 'sap_integration_db'
)\gexec

SELECT 'CREATE DATABASE supplier_agent_db'
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = 'supplier_agent_db'
)\gexec

-- ---------------------------------------------------------------------------
-- Supplier bounded context
-- ---------------------------------------------------------------------------
\connect supplier_db

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id         UUID PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    email               VARCHAR(320) NOT NULL,
    phone               VARCHAR(50) NOT NULL,
    tax_id              VARCHAR(100) NOT NULL,
    normalized_tax_id   VARCHAR(100) NOT NULL,
    status              VARCHAR(30) NOT NULL,
    street              VARCHAR(200) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    state               VARCHAR(100) NOT NULL,
    zip_code            VARCHAR(30) NOT NULL,
    country             VARCHAR(100) NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Align older local schemas with the current Supplier model.
CREATE UNIQUE INDEX IF NOT EXISTS uq_suppliers_normalized_tax_id
    ON suppliers (normalized_tax_id);

CREATE INDEX IF NOT EXISTS ix_suppliers_normalized_tax_id
    ON suppliers (normalized_tax_id);

ALTER TABLE suppliers
    DROP CONSTRAINT IF EXISTS ck_suppliers_status;

UPDATE suppliers
SET status = UPPER(status)
WHERE status IN ('draft', 'under_review', 'approved', 'rejected');

ALTER TABLE suppliers
    ADD CONSTRAINT ck_suppliers_status
    CHECK (status IN ('DRAFT', 'UNDER_REVIEW', 'APPROVED', 'REJECTED'));

CREATE TABLE IF NOT EXISTS supplier_onboarding_workflow (
    workflow_id              UUID PRIMARY KEY,
    correlation_id           UUID NOT NULL,
    idempotency_key          UUID NOT NULL,
    supplier_id              UUID NOT NULL,
    status                   VARCHAR(30) NOT NULL,
    service_now_ticket_id    VARCHAR(100),
    sap_business_partner_id  VARCHAR(100),
    rejection_reason         VARCHAR(1000),
    failure_reason           VARCHAR(1000),
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_supplier_onboarding_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES suppliers (supplier_id)
        ON DELETE RESTRICT
);

-- Backfill columns introduced by later project versions when aligning an
-- already-created local database.
ALTER TABLE supplier_onboarding_workflow
    ADD COLUMN IF NOT EXISTS correlation_id UUID;

UPDATE supplier_onboarding_workflow
SET correlation_id = gen_random_uuid()
WHERE correlation_id IS NULL;

ALTER TABLE supplier_onboarding_workflow
    ALTER COLUMN correlation_id SET NOT NULL;

ALTER TABLE supplier_onboarding_workflow
    ADD COLUMN IF NOT EXISTS idempotency_key UUID;

UPDATE supplier_onboarding_workflow
SET idempotency_key = gen_random_uuid()
WHERE idempotency_key IS NULL;

ALTER TABLE supplier_onboarding_workflow
    ALTER COLUMN idempotency_key SET NOT NULL;

ALTER TABLE supplier_onboarding_workflow
    DROP CONSTRAINT IF EXISTS ck_supplier_onboarding_status;

ALTER TABLE supplier_onboarding_workflow
    ADD CONSTRAINT ck_supplier_onboarding_status
    CHECK (
        status IN (
            'pending',
            'analyzing',
            'waiting_human_review',
            'syncing_to_sap',
            'completed',
            'rejected',
            'failed'
        )
    );

CREATE INDEX IF NOT EXISTS ix_supplier_onboarding_supplier_id
    ON supplier_onboarding_workflow (supplier_id);

CREATE INDEX IF NOT EXISTS ix_supplier_onboarding_correlation_id
    ON supplier_onboarding_workflow (correlation_id);

CREATE INDEX IF NOT EXISTS ix_supplier_onboarding_status
    ON supplier_onboarding_workflow (status);

CREATE UNIQUE INDEX IF NOT EXISTS uq_supplier_onboarding_workflow_idempotency_key
    ON supplier_onboarding_workflow (idempotency_key);

CREATE UNIQUE INDEX IF NOT EXISTS uq_supplier_onboarding_workflow_active_supplier
    ON supplier_onboarding_workflow (supplier_id)
    WHERE status NOT IN ('failed', 'rejected');

CREATE TABLE IF NOT EXISTS outbox_messages (
    message_id      UUID PRIMARY KEY,
    event_type      VARCHAR(200) NOT NULL,
    payload         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ,
    attempts        INTEGER NOT NULL DEFAULT 0
);

ALTER TABLE outbox_messages
    ADD COLUMN IF NOT EXISTS attempts INTEGER;

UPDATE outbox_messages
SET attempts = 0
WHERE attempts IS NULL;

ALTER TABLE outbox_messages
    ALTER COLUMN attempts SET DEFAULT 0,
    ALTER COLUMN attempts SET NOT NULL;

ALTER TABLE outbox_messages
    DROP CONSTRAINT IF EXISTS ck_supplier_outbox_attempts;

ALTER TABLE outbox_messages
    ADD CONSTRAINT ck_supplier_outbox_attempts CHECK (attempts >= 0);

CREATE INDEX IF NOT EXISTS ix_supplier_outbox_pending
    ON outbox_messages (created_at)
    WHERE processed_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_supplier_outbox_event_type
    ON outbox_messages (event_type);

CREATE INDEX IF NOT EXISTS ix_supplier_outbox_processed_at
    ON outbox_messages (processed_at);

CREATE TABLE IF NOT EXISTS inbox_messages (
    message_id      UUID PRIMARY KEY,
    event_type      VARCHAR(200) NOT NULL,
    processed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE inbox_messages
    ADD COLUMN IF NOT EXISTS processed_at TIMESTAMPTZ;

UPDATE inbox_messages
SET processed_at = NOW()
WHERE processed_at IS NULL;

ALTER TABLE inbox_messages
    ALTER COLUMN processed_at SET DEFAULT NOW(),
    ALTER COLUMN processed_at SET NOT NULL;

CREATE INDEX IF NOT EXISTS ix_supplier_inbox_event_type
    ON inbox_messages (event_type);

CREATE INDEX IF NOT EXISTS ix_supplier_inbox_processed_at
    ON inbox_messages (processed_at);

-- ---------------------------------------------------------------------------
-- SAP Integration bounded context
-- ---------------------------------------------------------------------------
\connect sap_integration_db

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS inbox_messages (
    message_id      UUID PRIMARY KEY,
    event_type      VARCHAR(200) NOT NULL,
    processed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE inbox_messages
    ADD COLUMN IF NOT EXISTS processed_at TIMESTAMPTZ;

UPDATE inbox_messages
SET processed_at = NOW()
WHERE processed_at IS NULL;

ALTER TABLE inbox_messages
    ALTER COLUMN processed_at SET DEFAULT NOW(),
    ALTER COLUMN processed_at SET NOT NULL;

CREATE INDEX IF NOT EXISTS ix_sap_inbox_event_type
    ON inbox_messages (event_type);

CREATE INDEX IF NOT EXISTS ix_sap_inbox_processed_at
    ON inbox_messages (processed_at);

CREATE TABLE IF NOT EXISTS sap_sync_operations (
    operation_id           UUID PRIMARY KEY,
    message_id             UUID NOT NULL,
    correlation_id         UUID NOT NULL,
    workflow_id            UUID NOT NULL,
    supplier_id            UUID NOT NULL,
    tax_id                 VARCHAR(100) NOT NULL,
    status                 VARCHAR(30) NOT NULL,
    business_partner_id    VARCHAR(100),
    sap_supplier_id        VARCHAR(100),
    attempts               INTEGER NOT NULL DEFAULT 0,
    failure_reason         TEXT,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE sap_sync_operations
    ADD COLUMN IF NOT EXISTS correlation_id UUID;

UPDATE sap_sync_operations
SET correlation_id = gen_random_uuid()
WHERE correlation_id IS NULL;

ALTER TABLE sap_sync_operations
    ALTER COLUMN correlation_id SET NOT NULL;

ALTER TABLE sap_sync_operations
    ADD COLUMN IF NOT EXISTS attempts INTEGER;

UPDATE sap_sync_operations
SET attempts = 0
WHERE attempts IS NULL;

ALTER TABLE sap_sync_operations
    ALTER COLUMN attempts SET DEFAULT 0,
    ALTER COLUMN attempts SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_sap_sync_operations_message_id
    ON sap_sync_operations (message_id);

ALTER TABLE sap_sync_operations
    DROP CONSTRAINT IF EXISTS ck_sap_sync_status;

ALTER TABLE sap_sync_operations
    ADD CONSTRAINT ck_sap_sync_status
    CHECK (status IN ('pending', 'processing', 'completed', 'failed'));

ALTER TABLE sap_sync_operations
    DROP CONSTRAINT IF EXISTS ck_sap_sync_attempts;

ALTER TABLE sap_sync_operations
    ADD CONSTRAINT ck_sap_sync_attempts CHECK (attempts >= 0);

CREATE INDEX IF NOT EXISTS ix_sap_sync_operations_correlation_id
    ON sap_sync_operations (correlation_id);

CREATE INDEX IF NOT EXISTS ix_sap_sync_operations_workflow_id
    ON sap_sync_operations (workflow_id);

CREATE INDEX IF NOT EXISTS ix_sap_sync_operations_supplier_id
    ON sap_sync_operations (supplier_id);

CREATE INDEX IF NOT EXISTS ix_sap_sync_operations_tax_id
    ON sap_sync_operations (tax_id);

CREATE INDEX IF NOT EXISTS ix_sap_sync_operations_status
    ON sap_sync_operations (status);

CREATE TABLE IF NOT EXISTS outbox_messages (
    message_id      UUID PRIMARY KEY,
    event_type      VARCHAR(200) NOT NULL,
    payload         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ,
    attempts        INTEGER NOT NULL DEFAULT 0
);

ALTER TABLE outbox_messages
    ADD COLUMN IF NOT EXISTS attempts INTEGER;

UPDATE outbox_messages
SET attempts = 0
WHERE attempts IS NULL;

ALTER TABLE outbox_messages
    ALTER COLUMN attempts SET DEFAULT 0,
    ALTER COLUMN attempts SET NOT NULL;

ALTER TABLE outbox_messages
    DROP CONSTRAINT IF EXISTS ck_sap_outbox_attempts;

ALTER TABLE outbox_messages
    ADD CONSTRAINT ck_sap_outbox_attempts CHECK (attempts >= 0);

CREATE INDEX IF NOT EXISTS ix_sap_outbox_pending
    ON outbox_messages (created_at)
    WHERE processed_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_sap_outbox_event_type
    ON outbox_messages (event_type);

CREATE INDEX IF NOT EXISTS ix_sap_outbox_processed_at
    ON outbox_messages (processed_at);

-- ---------------------------------------------------------------------------
-- Agent runtime database
-- ---------------------------------------------------------------------------
\connect supplier_agent_db

-- LangGraph owns its checkpoint tables. The Agent API calls
-- AsyncPostgresSaver.setup() during startup, so no domain tables are created here.

-- ---------------------------------------------------------------------------
-- Verification summary
-- ---------------------------------------------------------------------------
\connect supplier_db
SELECT current_database() AS database, COUNT(*) AS public_tables
FROM information_schema.tables
WHERE table_schema = 'public';

\connect sap_integration_db
SELECT current_database() AS database, COUNT(*) AS public_tables
FROM information_schema.tables
WHERE table_schema = 'public';

\connect supplier_agent_db
SELECT current_database() AS database, COUNT(*) AS public_tables
FROM information_schema.tables
WHERE table_schema = 'public';
