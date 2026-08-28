# Architecture consolidation summary

This document captures the major architecture decisions represented by the current repository.

## Standard integration-event envelope

SAP integration messages use a versioned envelope with:

- `message_id`: identity of one integration message;
- `correlation_id`: identity of the end-to-end onboarding business flow;
- `event_type`: versioned integration-event name;
- `version`: contract version;
- `occurred_at`: event timestamp;
- `payload`: event-specific data.

The Outbox record key uses the same `message_id` as the integration event.

## Reliability boundaries

- Transactional Outbox in Supplier and SAP Integration contexts.
- Inbox/processed-message tracking in inbound consumers.
- SQS acknowledgement only after local persistence succeeds.
- At-least-once publishing/consumption assumptions.
- DLQ topology with configured redrive policy.
- Structured failure logs include delivery metadata where available.
- Durable onboarding idempotency protects synchronous workflow start requests.

## AI governance

- Bedrock/RAG output is a recommendation.
- Deterministic application rules decide whether the business workflow can proceed.
- Business Human-in-the-Loop handles risky/uncertain supplier onboarding.
- LangGraph Human-in-the-Loop independently gates Agent state-changing tools.
- MCP provides capability access rather than repository/database access.

## Database ownership

Supplier bounded context → `supplier_db`:

- `api-supplier`;
- `worker-supplier-outbox`;
- `consumer-supplier-sap-result`.

SAP Integration bounded context → `sap_integration_db`:

- `consumer-sap`;
- `worker-sap-outbox`.

Agent runtime → `supplier_agent_db`:

- LangGraph checkpoint/runtime state only.

No cross-database foreign keys or direct cross-bounded-context repository access are used.

## Database bootstrap consolidation

Local/reference database creation and schema alignment are consolidated in:

```text
database/init.sql
```

The previous numbered database scripts and `database/init/` subfolder are obsolete after this consolidation.

## Observability

- end-to-end business `correlation_id`;
- structured JSON runtime logs;
- optional OpenTelemetry/OTLP traces;
- SQS trace-context propagation;
- Jaeger + OpenTelemetry Collector for local inspection.

## Intentionally replaceable adapters

The repository keeps fake SAP and ServiceNow integrations for demonstration. Application slices depend on gateway/protocol boundaries so production adapters can be introduced without moving those external concerns into domain logic.
