"""
Metric app: simulates a messy web server with Counters, Gauges, and Histograms.
Used to teach Prometheus metric types and PromQL.
"""
import random
import signal
import sys
import time

from prometheus_client import Counter, Gauge, Histogram, start_http_server

# --- Metrics ---

# Counter: total HTTP requests, broken down by status (200 vs 500)
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["status"],
)

# Gauge: current in-progress requests (simulated "active users")
in_progress_requests = Gauge(
    "in_progress_requests",
    "Number of requests currently being processed",
)

# Histogram: request duration in seconds (buckets for percentile queries)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "Request duration in seconds",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

_shutdown = False


def _signal_handler(signum, frame):
    global _shutdown
    _shutdown = True


def main():
    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    start_http_server(8000)
    print("Metrics server listening on :8000", flush=True)

    try:
        while not _shutdown:
            # Simulate "active users" — gauge is a point-in-time value
            in_progress_requests.set(random.randint(0, 10))

            # Time the "request" (sleep = processing)
            with http_request_duration_seconds.time():
                if random.random() < 0.10:
                    time.sleep(2.5)  # 10% slow query
                else:
                    time.sleep(random.uniform(0.05, 1.0))

            # 80% success, 20% error
            if random.random() < 0.80:
                http_requests_total.labels(status="200").inc()
            else:
                http_requests_total.labels(status="500").inc()

            print("Request processed", flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        print("Shutting down", flush=True)
        sys.exit(0)


if __name__ == "__main__":
    main()
