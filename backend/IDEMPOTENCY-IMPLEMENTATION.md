# Supplier onboarding idempotency

The onboarding write path carries a caller-provided `Idempotency-Key` through MCP/API Gateway to `api-supplier` and persists it with the onboarding workflow.

The LangGraph Agent deliberately hides this technical argument from the LLM. For Agent-originated onboarding, the runtime creates a UUID idempotency key before invoking the MCP tool.

## Guarantees

- Same `Idempotency-Key` + same supplier returns the existing workflow without repeating AI, review, SAP scheduling or Outbox side effects.
- Same `Idempotency-Key` + different supplier returns HTTP `409` (`idempotency_key_conflict`).
- A different key for a supplier that already has a non-failed/non-rejected workflow preserves the business invariant and returns HTTP `409`.
- PostgreSQL uniqueness on `idempotency_key` protects concurrent duplicate requests.
- A partial unique index protects against concurrent active onboarding workflows for the same supplier.
- `failed` and `rejected` workflows remain retryable with a new business intention/idempotency key.

## Database schema

Fresh/local environments receive the idempotency column and indexes through the consolidated:

```text
database/init.sql
```

For controlled upgrades of an already deployed Supplier database, the repository still keeps the application migration:

```text
backend/api-supplier/migrations/20260823_add_onboarding_idempotency.sql
```

The bootstrap script is for local/reference environments; production schema evolution should continue to use an explicit migration process.

## HTTP example

```http
POST /api/v1/suppliers/{supplier_id}/onboarding
Idempotency-Key: 11111111-2222-3333-4444-555555555555
```

Reuse the same key when retrying the **same logical request**. A new user/business intention should use a new key.

## Why the LLM does not receive the key

Idempotency is a platform reliability concern, not a business decision. The model expresses intent:

```text
start_supplier_onboarding(supplier_id)
```

The application/runtime supplies the technical idempotency key outside the model's tool schema. This reduces prompt/tool complexity and prevents the model from inventing reliability metadata.
