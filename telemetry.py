"""OpenTelemetry setup shared by the Flask and gRPC servers."""

import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from flask import request


def configure(app):
    """Instrument Flask and gRPC and export telemetry over OTLP/gRPC."""
    resource = Resource.create(
        {
            "service.name": os.getenv("OTEL_SERVICE_NAME", "python-simple-app"),
            "service.version": os.getenv("SERVICE_VERSION", "0.1.0"),
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter())
    )
    trace.set_tracer_provider(tracer_provider)

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(),
        export_interval_millis=int(
            os.getenv("OTEL_METRIC_EXPORT_INTERVAL", "60000")
        ),
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    request_counter = metrics.get_meter("python-simple-app").create_counter(
        "http.server.requests",
        description="Number of HTTP requests handled by the application",
    )

    @app.after_request
    def record_request(response):
        route = request_rule(app)
        request_counter.add(
            1,
            {"http.route": route, "http.status_code": response.status_code},
        )
        return response

    FlaskInstrumentor().instrument_app(app)
    GrpcInstrumentorServer().instrument()
    return tracer_provider, meter_provider


def request_rule(app):
    """Return a stable route label instead of recording request URLs."""
    return request.url_rule.rule if request.url_rule else "unknown"


def shutdown(providers):
    """Flush pending telemetry before the application exits."""
    tracer_provider, meter_provider = providers
    tracer_provider.shutdown()
    meter_provider.shutdown()
