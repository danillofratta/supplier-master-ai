# Final architecture changes

## Messaging contract

All SAP integration messages now use the same envelope:

- `message_id`: identity of one integration message.
- `correlation_id`: identity propagated through the complete onboarding flow.
- `event_type`: versioned integration event name.
- `version`: contract version.
- `occurred_at`: event timestamp.
- `payload`: event-specific data.

The Outbox primary key uses the same `message_id` as the integration event.

## Reliability

- Transactional Outbox in Supplier and SAP Integration.
- Inbox/idempotency in both inbound consumers.
- SQS messages are acknowledged only after local DB commit.
- Failed messages remain in SQS for retry.
- DLQs use `maxReceiveCount=5`.
- Approximate receive count is included in structured error logs.
- Consumers validate required message fields before invoking application handlers.

## Observability

- End-to-end `correlation_id`.
- Structured JSON runtime logs.
- Optional OpenTelemetry/OTLP support through the `observability` dependency
  group and `OTEL_EXPORTER_OTLP_ENDPOINT`.

## Database ownership

Supplier bounded context -> `supplier_db`:

- `api-supplier`
- `worker-supplier-outbox`
- `consumer-supplier-sap-result`

SAP Integration bounded context -> `sap_integration_db`:

- `consumer-sap`
- `worker-sap-outbox`

No cross-database foreign keys or direct cross-service repository access.

## Intentionally fake

The SAP network adapter remains `FakeSapGateway`. The application slice
depends on the `SapGateway` protocol, so a real SAP/OData adapter can replace
it without changing the use case.
