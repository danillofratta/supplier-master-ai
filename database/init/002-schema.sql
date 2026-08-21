\connect supplier_db
-- Complete schema for the Supplier bounded context.
-- Run against supplier_db.

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
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_suppliers_normalized_tax_id
        UNIQUE (normalized_tax_id),

    CONSTRAINT ck_suppliers_status
        CHECK (
            status IN (
                'DRAFT',
                'UNDER_REVIEW',
                'APPROVED',
                'REJECTED'
            )
        )
);

CREATE INDEX IF NOT EXISTS ix_suppliers_normalized_tax_id
    ON suppliers (normalized_tax_id);

CREATE TABLE IF NOT EXISTS supplier_onboarding_workflow (
    workflow_id              UUID PRIMARY KEY,
    correlation_id           UUID NOT NULL,
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
        ON DELETE RESTRICT,

    CONSTRAINT ck_supplier_onboarding_status
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
        )
);

CREATE INDEX IF NOT EXISTS ix_supplier_onboarding_supplier_id
    ON supplier_onboarding_workflow (supplier_id);

CREATE INDEX IF NOT EXISTS ix_supplier_onboarding_correlation_id
    ON supplier_onboarding_workflow (correlation_id);

CREATE INDEX IF NOT EXISTS ix_supplier_onboarding_status
    ON supplier_onboarding_workflow (status);

-- Transactional Outbox owned by Supplier.
CREATE TABLE IF NOT EXISTS outbox_messages (
    message_id      UUID PRIMARY KEY,
    event_type      VARCHAR(200) NOT NULL,
    payload         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ,
    attempts        INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT ck_supplier_outbox_attempts
        CHECK (attempts >= 0)
);

CREATE INDEX IF NOT EXISTS ix_supplier_outbox_pending
    ON outbox_messages (created_at)
    WHERE processed_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_supplier_outbox_event_type
    ON outbox_messages (event_type);

-- Inbox for result consumers that update Supplier state.
CREATE TABLE IF NOT EXISTS inbox_messages (
    message_id      UUID PRIMARY KEY,
    event_type      VARCHAR(200) NOT NULL,
    processed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_supplier_inbox_event_type
    ON inbox_messages (event_type);

CREATE INDEX IF NOT EXISTS ix_supplier_inbox_processed_at
    ON inbox_messages (processed_at);

\connect sap_integration_db
-- Complete schema for the SAP Integration bounded context.
-- Run against sap_integration_db.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Inbox / idempotency for SQS request messages.
CREATE TABLE IF NOT EXISTS inbox_messages (
    message_id      UUID PRIMARY KEY,
    event_type      VARCHAR(200) NOT NULL,
    processed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_sap_inbox_event_type
    ON inbox_messages (event_type);

CREATE INDEX IF NOT EXISTS ix_sap_inbox_processed_at
    ON inbox_messages (processed_at);

-- Persistent state of a SAP synchronization.
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
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_sap_sync_operations_message_id
        UNIQUE (message_id),

    CONSTRAINT ck_sap_sync_status
        CHECK (
            status IN (
                'pending',
                'processing',
                'completed',
                'failed'
            )
        ),

    CONSTRAINT ck_sap_sync_attempts
        CHECK (attempts >= 0)
);

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

-- Transactional result Outbox owned by SAP Integration.
CREATE TABLE IF NOT EXISTS outbox_messages (
    message_id      UUID PRIMARY KEY,
    event_type      VARCHAR(200) NOT NULL,
    payload         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ,
    attempts        INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT ck_sap_outbox_attempts
        CHECK (attempts >= 0)
);

CREATE INDEX IF NOT EXISTS ix_sap_outbox_pending
    ON outbox_messages (created_at)
    WHERE processed_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_sap_outbox_event_type
    ON outbox_messages (event_type);
