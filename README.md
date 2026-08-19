# Supplier Master AI

A microservice-oriented reference implementation for an AI-assisted Supplier
Master onboarding workflow using Python, FastAPI, RAG, PostgreSQL, AWS SQS,
Transactional Outbox/Inbox, idempotency and SAP integration boundaries.

## Deployables

```text
backend/
├── api-supplier/
├── worker-supplier-outbox/
├── consumer-sap/
├── worker-sap-outbox/
└── consumer-supplier-sap-result/
```

## Bounded contexts and database ownership

### Supplier

Uses `supplier_db`.

- `api-supplier`
- `worker-supplier-outbox`
- `consumer-supplier-sap-result`

### SAP Integration

Uses `sap_integration_db`.

- `consumer-sap`
- `worker-sap-outbox`

There is no cross-service database access between Supplier and SAP
Integration.

## Event flow

```text
api-supplier
  -> supplier_db / transactional outbox
  -> worker-supplier-outbox
  -> SQS supplier-sap-sync-requests
  -> consumer-sap
  -> sap_integration_db / inbox + operation + outbox
  -> worker-sap-outbox
  -> SQS supplier-sap-sync-results
  -> consumer-supplier-sap-result
  -> supplier_db
```

Integration events use a common envelope:

```json
{
  "message_id": "uuid",
  "correlation_id": "uuid",
  "event_type": "supplier.sap-sync.requested.v1",
  "version": 1,
  "occurred_at": "ISO-8601",
  "payload": {}
}
```

`message_id` identifies one message. `correlation_id` follows the complete
onboarding flow across services. `workflow_id` identifies the persisted
business workflow.

See `database/README.md` for PostgreSQL setup and
`docs/RUN_MESSAGING_FLOW.md` for the runtime flow.

## API Gateway

The frontend talks only to `api-gateway` on port `8000`. The gateway routes Supplier requests to `api-supplier` on port `8001`, creates or propagates `X-Correlation-ID`, forwards `Authorization`, applies downstream timeouts, exposes readiness/liveness checks and centralizes frontend CORS.

Public Supplier routes:

```text
GET  /api/v1/suppliers
POST /api/v1/suppliers
GET  /api/v1/suppliers/{supplier_id}
POST /api/v1/suppliers/{supplier_id}/analysis
GET  /api/v1/suppliers/{supplier_id}/onboarding
```

See `backend/api-gateway/README.md` for local execution.
