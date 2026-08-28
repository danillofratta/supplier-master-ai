# Observability

Supplier Master AI uses structured logging, business correlation identifiers and optional OpenTelemetry tracing across the independently deployable backend processes.

## Identity model

The system intentionally keeps four identifiers separate:

| Identifier | Meaning |
|---|---|
| `trace_id` | One technical distributed trace segment |
| `correlation_id` | One long-running supplier onboarding business flow |
| `message_id` | One integration event/message |
| `thread_id` | One LangGraph Agent conversation/checkpoint stream |

A long-running onboarding can outlive a single HTTP trace, so `correlation_id` is the primary business-flow correlation key.

## Structured logging

Backend runtime logs are JSON and can include, when available:

```text
timestamp
level
service
logger
message
correlation_id
trace_id
span_id
feature
component
supplier_id
workflow_id
message_id
event_type
duration_ms
```

Exceptions include stack traces. HTTP request middleware logs request lifecycle events without logging request bodies, prompts, credentials or policy contents.

## OpenTelemetry

The shared observability helpers support:

- OTLP HTTP export through `OTEL_EXPORTER_OTLP_ENDPOINT`;
- FastAPI instrumentation;
- HTTPX instrumentation;
- SQLAlchemy instrumentation;
- Botocore/Boto3 instrumentation;
- manual feature/component spans;
- W3C trace-context propagation over SQS message attributes.

The local Compose stack includes OpenTelemetry Collector and Jaeger.

## Supplier AI trace example

A supplier analysis can produce a hierarchy similar to:

```text
HTTP POST /v1/suppliers/{id}/analysis
└── feature.AnalyzeSupplier
    ├── repository.supplier.get_by_id
    ├── rag.policy_retrieval
    │   ├── embedding.generate
    │   └── opensearch.search
    └── ai.supplier_analysis
        └── bedrock.supplier_analysis
```

Logs around these spans can capture safe operational metadata such as duration, model ID, retrieved document count, risk level, recommended action and confidence. Prompts, policy text and secrets should not be emitted.

## Messaging traces

Outbox workers create producer spans and inject W3C trace context into SQS message attributes. Consumers extract those attributes before creating consumer spans.

The Transactional Outbox creates an intentional asynchronous boundary: the HTTP transaction that stores an Outbox message and the later worker publication may be separate trace roots because trace context is not persisted in the Outbox schema. `correlation_id` links those segments at the business-flow level.

## Installation

`api-supplier` includes observability dependencies through its runtime/all extras. Other independently deployed services expose an `observability` optional dependency group where applicable.

Examples:

```powershell
cd backend\api-supplier
python -m pip install -e ".[all]"
```

```powershell
cd backend\worker-supplier-outbox
python -m pip install -e ".[observability]"
```

The logging layer remains usable when optional OpenTelemetry packages are unavailable; tracing helpers are designed to degrade to no-op behavior.

## Local viewing

With the core Compose stack running:

- Jaeger UI: `http://localhost:16686`
- OTLP HTTP Collector endpoint used by containers: `http://otel-collector:4318`

## Production hardening

For production, add centralized log retention, access controls, sampling policy, trace/log redaction tests, alerting, SLOs and dashboards for queue lag, DLQ depth, Agent failures, AI latency/cost and SAP synchronization outcomes.
