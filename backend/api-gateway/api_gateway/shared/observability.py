from __future__ import annotations

import os
from contextvars import ContextVar, Token
from typing import Any


_CORRELATION_ID: ContextVar[str] = ContextVar(
    "correlation_id",
    default="-",
)


def set_correlation_id(
    correlation_id: str | None,
) -> Token:
    return _CORRELATION_ID.set(
        correlation_id or "-"
    )


def reset_correlation_id(
    token: Token,
) -> None:
    _CORRELATION_ID.reset(token)


def get_correlation_id() -> str:
    return _CORRELATION_ID.get()


def current_trace_fields() -> dict[str, str]:
    try:
        from opentelemetry import trace

        context = trace.get_current_span().get_span_context()
        if not context.is_valid:
            return {}

        return {
            "trace_id": format(
                context.trace_id,
                "032x",
            ),
            "span_id": format(
                context.span_id,
                "016x",
            ),
        }
    except ImportError:
        return {}


def get_tracer(
    service_name: str,
):
    try:
        from opentelemetry import trace
        return trace.get_tracer(service_name)
    except ImportError:
        return _NullTracer()


def configure_tracing(
    service_name: str,
):
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import (
            Resource,
        )
        from opentelemetry.sdk.trace import (
            TracerProvider,
        )
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
        )
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
    except ImportError:
        return _NullTracer()

    provider = trace.get_tracer_provider()

    # Only install an SDK provider when another one has not already
    # been configured by the runtime/auto-instrumentation.
    if provider.__class__.__module__.startswith(
        "opentelemetry.trace"
    ):
        provider = TracerProvider(
            resource=Resource.create(
                {
                    "service.name": service_name,
                }
            )
        )

        endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT"
        )
        if endpoint:
            exporter = OTLPSpanExporter(
                endpoint=endpoint.rstrip("/")
                + "/v1/traces"
            )
            provider.add_span_processor(
                BatchSpanProcessor(exporter)
            )

        trace.set_tracer_provider(provider)

    return trace.get_tracer(service_name)


def instrument_fastapi(
    app: Any,
) -> None:
    try:
        from opentelemetry.instrumentation.fastapi import (
            FastAPIInstrumentor,
        )

        FastAPIInstrumentor.instrument_app(app)
    except ImportError:
        return


def instrument_httpx() -> None:
    try:
        from opentelemetry.instrumentation.httpx import (
            HTTPXClientInstrumentor,
        )

        HTTPXClientInstrumentor().instrument()
    except ImportError:
        return


def instrument_sqlalchemy(
    engine: Any,
) -> None:
    try:
        from opentelemetry.instrumentation.sqlalchemy import (
            SQLAlchemyInstrumentor,
        )

        SQLAlchemyInstrumentor().instrument(
            engine=engine.sync_engine,
        )
    except ImportError:
        return


def instrument_botocore() -> None:
    try:
        from opentelemetry.instrumentation.botocore import (
            BotocoreInstrumentor,
        )

        BotocoreInstrumentor().instrument()
    except ImportError:
        return


def inject_sqs_trace_attributes(
    attributes: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    try:
        from opentelemetry.propagate import inject

        carrier: dict[str, str] = {}
        inject(carrier)

        for key in (
            "traceparent",
            "tracestate",
            "baggage",
        ):
            value = carrier.get(key)
            if value:
                attributes[key] = {
                    "DataType": "String",
                    "StringValue": value,
                }
    except ImportError:
        pass

    return attributes


def extract_sqs_trace_context(
    message: dict[str, Any],
):
    try:
        from opentelemetry.propagate import extract

        message_attributes = message.get(
            "MessageAttributes",
            {},
        )

        carrier = {
            key: value["StringValue"]
            for key, value in message_attributes.items()
            if isinstance(value, dict)
            and value.get("StringValue")
            and key in {
                "traceparent",
                "tracestate",
                "baggage",
            }
        }

        return extract(carrier)
    except ImportError:
        return None


def start_consumer_span(
    tracer: Any,
    name: str,
    message: dict[str, Any],
):
    context = extract_sqs_trace_context(
        message
    )

    try:
        from opentelemetry.trace import SpanKind

        return tracer.start_as_current_span(
            name,
            context=context,
            kind=SpanKind.CONSUMER,
        )
    except ImportError:
        return tracer.start_as_current_span(name)


def start_producer_span(
    tracer: Any,
    name: str,
):
    try:
        from opentelemetry.trace import SpanKind

        return tracer.start_as_current_span(
            name,
            kind=SpanKind.PRODUCER,
        )
    except ImportError:
        return tracer.start_as_current_span(name)


def record_exception(
    span: Any,
    exc: BaseException,
) -> None:
    try:
        from opentelemetry.trace import (
            Status,
            StatusCode,
        )

        span.record_exception(exc)
        span.set_status(
            Status(
                StatusCode.ERROR,
                str(exc),
            )
        )
    except (ImportError, AttributeError):
        return


class _NullSpan:
    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> None:
        return None

    def record_exception(
        self,
        exc: BaseException,
    ) -> None:
        return None

    def set_status(
        self,
        status: Any,
    ) -> None:
        return None


class _NullTracer:
    def start_as_current_span(
        self,
        name: str,
        *args,
        **kwargs,
    ):
        return _NullSpanContext()


class _NullSpanContext:
    def __enter__(self):
        return _NullSpan()

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> bool:
        return False
