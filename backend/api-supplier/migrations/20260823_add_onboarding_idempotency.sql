-- Adds durable idempotency to supplier onboarding.
-- Apply this once to an existing supplier_db before deploying the updated API.
-- PostgreSQL 13+ provides gen_random_uuid() natively.

BEGIN;

ALTER TABLE supplier_onboarding_workflow
    ADD COLUMN IF NOT EXISTS idempotency_key UUID;

-- Existing workflows predate idempotency. Give each historical row a unique
-- synthetic key so the new column can safely become NOT NULL.
UPDATE supplier_onboarding_workflow
SET idempotency_key = gen_random_uuid()
WHERE idempotency_key IS NULL;

ALTER TABLE supplier_onboarding_workflow
    ALTER COLUMN idempotency_key SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS
    uq_supplier_onboarding_workflow_idempotency_key
ON supplier_onboarding_workflow (idempotency_key);

-- The application already prevents a second non-retryable onboarding for the
-- same supplier. This partial unique index makes that invariant concurrency-safe.
-- FAILED and REJECTED workflows remain retryable with a new idempotency key.
CREATE UNIQUE INDEX IF NOT EXISTS
    uq_supplier_onboarding_workflow_active_supplier
ON supplier_onboarding_workflow (supplier_id)
WHERE status NOT IN ('failed', 'rejected');

COMMIT;
