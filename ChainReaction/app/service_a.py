"""
Service-A (The Gateway): Receives user request, calls Service-B via HTTP.
Initial state: raw FastAPI, no tracing.
"""
import json
import logging
import sys

import httpx
from fastapi import FastAPI

app = FastAPI(title="Service-A (Gateway)")

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

# --- STEP 2: INSERT OTEL INSTRUMENTATION HERE ---
# (OTLPSpanExporter -> otel-collector:4317, FastAPIInstrumentor, RequestsInstrumentor, trace_id in logs)


@app.get("/")
async def root():
    """Entry point: call Service-B."""
    logger.info("Service-A received request", extra={"service": "service-a"})
    async with httpx.AsyncClient() as client:
        r = await client.get("http://service-b:8000/request")
    return {"service": "A", "upstream": r.json(), "status": r.status_code}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "A"}
