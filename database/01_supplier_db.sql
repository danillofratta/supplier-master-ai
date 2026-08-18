-- Supplier bounded context
-- Database: supplier_db

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
        CHECK (status IN ('draft', 'under_review', 'approved', 'rejected'))
);

CREATE INDEX IF NOT EXISTS ix_suppliers_normalized_tax_id
    ON suppliers (normalized_tax_id);

CREATE TABLE IF NOT EXISTS supplier_onboarding_workflow (
    workflow_id              UUID PRIMARY KEY,
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

CREATE INDEX IF NOT EXISTS ix_supplier_onboarding_status
    ON supplier_onboarding_workflow (status);

CREATE TABLE IF NOT EXISTS outbox_messages (
    message_id      UUID PRIMARY KEY,
    event_type      VARCHAR(200) NOT NULL,
    payload         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ,
    attempts        INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT ck_outbox_attempts_non_negative
        CHECK (attempts >= 0)
);

CREATE INDEX IF NOT EXISTS ix_supplier_outbox_pending
    ON outbox_messages (created_at)
    WHERE processed_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_supplier_outbox_event_type
    ON outbox_messages (event_type);

-- Used by consumer-supplier-sap-result for idempotency.
CREATE TABLE IF NOT EXISTS inbox_messages (
    message_id      UUID PRIMARY KEY,
    event_type      VARCHAR(200) NOT NULL,
    processed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_supplier_inbox_event_type
    ON inbox_messages (event_type);

CREATE INDEX IF NOT EXISTS ix_supplier_inbox_processed_at
    ON inbox_messages (processed_at);
