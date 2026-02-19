"""
Flask app that exposes Prometheus metrics for the Grafana lab.
Counter: http_requests_total with labels method, endpoint, http_status.
"""
from flask import Flask
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Counter for HTTP requests — Grafana will visualize rate() of this
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"],
)


@app.route("/")
def hello():
    http_requests_total.labels(method="GET", endpoint="/", http_status="200").inc()
    return "Hello World"


@app.route("/error")
def error():
    http_requests_total.labels(method="GET", endpoint="/error", http_status="500").inc()
    return "Error", 500


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
