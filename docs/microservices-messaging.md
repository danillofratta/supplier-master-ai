# Microservices messaging boundary

## Services

### API Supplier

Owns:

- Supplier aggregate
- Supplier onboarding workflow
- PostgreSQL persistence
- Transactional outbox
- RAG / AI analysis
- workflow state

Processes:

1. API process
2. Outbox publisher process
3. SAP result consumer process

These processes may share the API Supplier code and database because they
belong to the same bounded context.

### Consumer SAP

Owns:

- SAP integration logic
- SAP-specific DTOs and adapters
- message idempotency
- reconciliation before SAP create

It does not import Supplier-service entities, repositories, Unit of Work, or
SQLAlchemy models.

## Integration contracts

Services communicate only through versioned JSON integration events:

- `supplier.sap-sync.requested.v1`
- `supplier.sap-sync.completed.v1`

The repository contains JSON Schema files under `/contracts` only as
language-neutral documentation/contract definitions. Each microservice has
its own local DTO representation.

## Transactional outbox

When a supplier is approved, the API Supplier performs one local
PostgreSQL transaction:

1. workflow -> `SYNCING_TO_SAP`
2. add `supplier.sap-sync.requested.v1` to the outbox
3. commit

No SAP call occurs inside this transaction.

The Outbox Processor runs independently, publishes pending records to the
message broker, and marks them processed.

Publishing is intentionally at-least-once. A crash after broker publish but
before `processed_at` is saved can publish a duplicate. Consumers therefore
must be idempotent.

## Consumer SAP idempotency

The Consumer SAP:

1. parses its own copy of the integration contract
2. checks whether `event_id` was already processed
3. reconciles by `tax_id` with SAP before creating
4. creates only when the supplier does not exist
5. publishes `supplier.sap-sync.completed.v1`
6. records the request event as processed

The reconciliation step handles the ambiguous-timeout case where SAP may
have created the supplier but the caller did not receive the response.

## Result flow

The API Supplier consumes the completion event in its own consumer
process and transitions:

`SYNCING_TO_SAP -> COMPLETED`

This preserves database ownership: the Consumer SAP never writes directly to
the Supplier database.
