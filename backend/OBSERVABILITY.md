# Observability

All backend deployables now follow the same observability pattern while
remaining independently deployable. Each service owns the same two local
modules:

```text
<service package>/shared/
├── logging.py
└── observability.py
```

No business rules, AI model configuration, prompts, environment values or
workflow decisions are changed by this layer.

## Structured logging

Runtime logs are JSON and include, when available:

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

Exceptions include their stack trace.

The HTTP services also log request start/completion/failure without logging
request bodies, prompts, credentials or supplier policy contents.

## OpenTelemetry

The standard helper supports:

- OTLP HTTP trace exporting through the already-supported
  `OTEL_EXPORTER_OTLP_ENDPOINT`.
- FastAPI auto-instrumentation.
- HTTPX client instrumentation.
- SQLAlchemy instrumentation.
- Botocore/Boto3 instrumentation.
- manual feature spans where domain/use-case visibility is useful.
- W3C trace context propagation over SQS through `traceparent`,
  `tracestate` and `baggage` message attributes.

## Supplier AI trace

A Supplier analysis now produces spans similar to:

```text
HTTP POST /v1/suppliers/{id}/analysis
└── feature.AnalyzeSupplier
    ├── repository.supplier.get_by_id
    ├── rag.policy_retrieval
    │   ├── opensearch.policy.retrieve
    │   │   ├── embedding.generate
    │   │   │   └── bedrock.embedding.generate
    │   │   └── opensearch.search
    └── ai.supplier_analysis
        └── bedrock.supplier_analysis
```

The logs emitted around these spans show document counts, duration, model ID,
risk, recommended action and confidence. Prompts and secrets are not logged.

## Messaging

The Outbox workers create producer spans. Before publishing to SQS they inject
the active W3C trace context into SQS message attributes.

The consumers extract that context and create consumer spans, so a publish and
its downstream consumption can appear in the same distributed trace.

`correlation_id` remains the business-flow correlation mechanism across the
entire onboarding flow.

Because the Transactional Outbox intentionally stores the integration event
and is later polled by a separate process, the HTTP request trace and the
Outbox worker trace are separate trace roots unless trace context is also
persisted in the Outbox record. This implementation deliberately does not
change the Outbox schema or integration-event business contract. The existing
`correlation_id` allows the two trace segments to be correlated operationally.

## Installation

`api-supplier` keeps the existing `all` extra and it now includes its
observability dependencies:

```cmd
python -m pip install -e ".[all]"
```

For the other independently deployed services:

```cmd
python -m pip install -e ".[observability]"
```

The application remains functional if the optional OpenTelemetry libraries are
not installed; structured logging still works and tracing helpers gracefully
fall back to no-op spans.

## No configuration changes

No `.env` values were changed. Existing values such as
`OTEL_EXPORTER_OTLP_ENDPOINT` continue to be used as before.
