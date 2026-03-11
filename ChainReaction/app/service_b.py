"""
Service-B (The Logic): Receives request, calls Service-C via HTTP.
Initial state: raw FastAPI, no tracing.
"""
import json
import logging
import sys

import httpx
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

app = FastAPI(title="Service-B (Logic)")

# --- Standard JSON logger to stdout ---
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "level": record.levelname.lower(),
            "msg": record.getMessage(),
            **{k: v for k, v in record.__dict__.items()
               if k not in ("name", "msg", "args", "levelname", "levelno", "pathname",
                            "filename", "module", "lineno", "funcName", "created",
                            "msecs", "relativeCreated", "thread", "threadName",
                            "message", "exc_info", "exc_text", "stack_info", "taskName") and v is not None}
        })

_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(JsonFormatter())
logging.getLogger().handlers.clear()
logging.getLogger().addHandler(_handler)
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# OTel: send spans to Collector -> Tempo
resource = Resource.create({"service.name": "service-b"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")))
trace.set_tracer_provider(provider)
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()

# Correlation key: add trace_id to every log line for Tempo <-> Loki
def trace_id_filter(record):
    span = trace.get_current_span()
    ctx = span.get_span_context()
    record.trace_id = format(ctx.trace_id, "032x") if ctx.is_valid else ""
    return True

logger.addFilter(trace_id_filter)


@app.get("/request")
async def request_handler():
    """Called by Service-A; calls Service-C."""
    logger.info("Service-B received request", extra={"service": "service-b"})
    async with httpx.AsyncClient() as client:
        r = await client.get("http://service-c:8000/request")
    return {"service": "B", "upstream": r.json(), "status": r.status_code}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "B"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
