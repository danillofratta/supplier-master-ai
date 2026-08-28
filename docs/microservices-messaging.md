# Microservices messaging boundary

## Purpose

Supplier Master AI separates Supplier ownership from SAP Integration ownership and uses versioned asynchronous messages rather than cross-database writes.

## Process ownership

### Supplier bounded context

Owns:

- Supplier aggregate/master data;
- Supplier onboarding workflow;
- `supplier_db`;
- Supplier Transactional Outbox;
- Supplier Inbox for SAP result messages;
- RAG/AI onboarding analysis.

Processes sharing this bounded context/database:

1. `api-supplier`;
2. `worker-supplier-outbox`;
3. `consumer-supplier-sap-result`.

Sharing the bounded-context database does not mean they bypass application ownership: they use context-specific repositories/Unit of Work implementations.

### SAP Integration bounded context

Owns:

- SAP-specific synchronization operation state;
- request Inbox/idempotency;
- SAP gateway adapter;
- SAP result Transactional Outbox;
- `sap_integration_db`.

Processes:

1. `consumer-sap`;
2. `worker-sap-outbox`.

It does not write directly to `supplier_db` or import Supplier persistence models.

## Integration contracts

Services communicate through versioned integration events, including:

- `supplier.sap-sync.requested.v1`;
- SAP synchronization completion/failure result events represented by the current contracts under `/contracts`.

The repository keeps JSON Schema definitions under `/contracts` as language-neutral contract documentation. Each service owns its local DTO/mapping representation.

## Message envelope

The standard envelope contains:

```text
message_id
correlation_id
event_type
version
occurred_at
payload
```

- `message_id` uniquely identifies one event for idempotency/diagnostics.
- `correlation_id` follows the complete onboarding business flow.

## Transactional Outbox — Supplier side

When a workflow is allowed to synchronize:

1. workflow transitions to `syncing_to_sap`;
2. the request integration event is stored in `outbox_messages`;
3. the Supplier transaction commits.

No SAP network call occurs inside this transaction.

The Supplier Outbox worker later publishes pending events and marks them processed. A crash after broker publish but before saving `processed_at` can publish a duplicate; the design therefore assumes at-least-once delivery.

## SAP consumer idempotency

The SAP consumer:

1. maps/validates its local message contract;
2. checks message identity/Inbox state;
3. persists/loads the SAP synchronization operation;
4. calls the SAP gateway boundary;
5. stores the SAP result event in the SAP Integration Outbox;
6. commits locally;
7. only then deletes the request message from SQS.

The fake SAP gateway stands in for a production SAP/OData adapter without moving ERP-specific concerns into the Supplier domain.

## Result flow

```text
sap_integration_db result Outbox
  ↓
worker-sap-outbox
  ↓
SQS result queue
  ↓
consumer-supplier-sap-result
  ↓ Inbox + workflow update
supplier_db
```

This preserves database ownership: SAP Integration never writes directly to Supplier persistence.

## Retry and DLQ

If a consumer fails before successful commit, the SQS message is left unacknowledged and becomes visible again after the visibility timeout. Inbox/idempotency prevents duplicate side effects, and the configured redrive policy moves repeatedly failing messages to a DLQ.

## Observability

SQS messages propagate business `correlation_id` in their event envelope. OpenTelemetry producer/consumer instrumentation can additionally propagate W3C trace context in SQS message attributes.
