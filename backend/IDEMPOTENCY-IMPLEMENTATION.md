# Supplier Onboarding Idempotency

The onboarding write path now carries a caller-provided `Idempotency-Key` from MCP through the API Gateway to `api-supplier` and persists it with the onboarding workflow.

## Guarantees

- Same `Idempotency-Key` + same supplier: returns the existing workflow and does not run AI, ServiceNow, SAP scheduling, or outbox side effects again.
- Same `Idempotency-Key` + different supplier: returns HTTP 409 (`idempotency_key_conflict`).
- Different key + supplier with an existing non-failed/non-rejected workflow: keeps the existing business invariant and returns HTTP 409.
- Concurrent duplicate requests are protected by a PostgreSQL unique constraint on `idempotency_key`.
- Concurrent attempts to start more than one non-retryable workflow for the same supplier are protected by a partial unique index.

## Database migration

Apply before deploying the updated `api-supplier` against an existing database:

`api-supplier/migrations/20260823_add_onboarding_idempotency.sql`

The migration backfills historical workflow rows with generated UUIDs, makes `idempotency_key` non-null, and creates the required unique indexes.

## Request example

```http
POST /api/v1/suppliers/{supplier_id}/onboarding
Idempotency-Key: 11111111-2222-3333-4444-555555555555
```

The key must be reused for retries of the same logical request. A new user/business intention should use a new key.
