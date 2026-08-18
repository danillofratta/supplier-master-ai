import os
from contextlib import nullcontext


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


class _NullSpan:
    def set_attribute(self, key, value):
        return None


class _NullTracer:
    def start_as_current_span(self, name):
        return _NullSpanContext()


class _NullSpanContext:
    def __enter__(self):
        return _NullSpan()

    def __exit__(self, exc_type, exc, traceback):
        return False
