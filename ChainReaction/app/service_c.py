"""
Service-C (The Database): Simulates a database call with time.sleep(2).
Initial state: raw FastAPI, no tracing.
"""
import json
import logging
import sys
import time

from fastapi import FastAPI

app = FastAPI(title="Service-C (Database)")

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
# (OTLPSpanExporter -> otel-collector:4317, FastAPIInstrumentor, trace_id in logs)


@app.get("/request")
async def request_handler():
    """Called by Service-B; simulates DB with 2s sleep."""
    logger.info("Service-C simulating DB call", extra={"service": "service-c"})
    time.sleep(2)  # The latency culprit
    return {"service": "C", "result": "ok", "simulated_db_ms": 2000}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "C"}
