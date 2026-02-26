"""
Payment Processor (Victim App) for 'The Poison Pill' observability lab.
Exposes Prometheus metrics and JSON logs to stdout for Loki.
"""
import json
import logging
import os
import sys

from flask import Flask, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- JSON logging to stdout only ---
class JsonFormatter(logging.Formatter):
    _STANDARD = frozenset(
        {"name", "msg", "args", "levelname", "levelno", "pathname", "filename",
         "module", "lineno", "funcName", "created", "msecs", "relativeCreated",
         "thread", "threadName", "message", "exc_info", "exc_text", "stack_info",
         "taskName", "message"}
    )

    def format(self, record):
        log_obj = {
            "level": record.levelname.lower(),
            "msg": record.getMessage(),
        }
        for k, v in record.__dict__.items():
            if k not in self._STANDARD and v is not None:
                log_obj[k] = v
        return json.dumps(log_obj)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
root = logging.getLogger()
root.handlers.clear()
root.addHandler(handler)
root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# --- Prometheus counter ---
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/checkout", methods=["GET"])
def checkout():
    item = request.args.get("item", "").strip() or "unknown"

    # The Poison Pill
    if item == "cursed_amulet":
        http_requests_total.labels(method="GET", endpoint="/checkout", status="500").inc()
        logger.error(
            "Payment Gateway Timeout",
            extra={"item": "cursed_amulet", "error_code": "ERR-999", "endpoint": "/checkout"},
        )
        return {"error": "Payment Gateway Timeout"}, 500

    # Happy path
    http_requests_total.labels(method="GET", endpoint="/checkout", status="200").inc()
    logger.info(
        "Payment successful",
        extra={"item": item, "endpoint": "/checkout"},
    )
    return {"status": "ok", "item": item}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
