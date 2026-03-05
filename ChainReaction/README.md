# The Chain Reaction — Capstone Lab

## Mission Brief

You will instrument a **3-tier microservice architecture** with **OpenTelemetry (OTel)**, route traces through an **OTel Collector** to **Grafana Tempo**, and correlate them with **Loki** logs. This is the standard pattern for production observability: one collector, one protocol (OTLP), and trace–log correlation in Grafana.

**The stack:**

- **Service-A** (Gateway) → **Service-B** (Logic) → **Service-C** (Database). Service-C simulates a 2-second “database” call.
- **OTel Collector**: receives OTLP from the apps, batches, and exports to Tempo. The *standard way* to handle telemetry at scale.
- **Tempo**: stores traces. **Loki**: stores logs. **Grafana**: queries both and links trace ↔ logs via TraceID.

---

## Prerequisites

- Kubernetes cluster (e.g. **Minikube**), **kubectl**, **Docker** (or similar).
- The lab is **self-contained**: you deploy Grafana, Tempo, and Loki in the same namespace. No existing Grafana or other stacks are required.

---

## Phase 1: The Blindness

**Goal:** Deploy the raw apps and the observability backend. See latency in Grafana but **zero traces** in Tempo.

### 1.1 Create namespace and infrastructure

```bash
kubectl apply -f k8s/0-otel-collector.yaml
kubectl apply -f k8s/1-tempo.yaml
kubectl apply -f k8s/2-loki.yaml
kubectl apply -f k8s/4-promtail.yaml
kubectl apply -f k8s/5-grafana.yaml
```

Wait until Pods are ready in `chain-reaction` (including **grafana**, **tempo**, **loki**, **otel-collector**).

### 1.2 Build and deploy the apps (no tracing yet)

From the **ChainReaction** folder:

```bash
eval $(minikube docker-env)
docker build -t chain-reaction-app:latest ./app
kubectl apply -f k8s/3-apps.yaml
```

### 1.3 Expose Service-A and generate traffic

Port-forward the gateway and hit it in a loop:

```bash
kubectl port-forward -n chain-reaction svc/service-a 8000:8000
# In another terminal:
while true; do curl -s http://localhost:8000/; sleep 1; done
```

You will see responses with ~2 seconds latency (A → B → C, and C sleeps 2s).

### 1.4 Open Grafana and add Tempo and Loki

Port-forward Grafana and open it in your browser:

```bash
kubectl port-forward -n chain-reaction svc/grafana 3000:3000
```

Open **http://localhost:3000**. Log in with **admin** / **admin** (change password if prompted).

Add two data sources (Connections → Data sources → Add data source):

- **Tempo:** Type **Tempo**, URL **`http://tempo:3200`** (Grafana is in the same namespace). Access: **Server**. Save & test.
- **Loki:** Type **Loki**, URL **`http://loki:3100`**. Access: **Server**. Save & test.

### 1.5 Observe the blindness

In Grafana **Explore**, select **Tempo** and run a search. You will see **no traces**: the apps are not instrumented. You feel the 2-second delay but cannot see *where* it comes from.

---

## Phase 2: The Instrumentation

**Goal:** Add OTel to each service so traces flow: App → OTel Collector → Tempo, and logs carry `trace_id` for correlation.

### 2.1 Dependencies

Add to `app/requirements.txt`:

```
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-http
opentelemetry-instrumentation-fastapi
opentelemetry-instrumentation-httpx
```

Rebuild the image after editing `requirements.txt`:

```bash
docker build -t chain-reaction-app:latest ./app
kubectl rollout restart deployment/service-a deployment/service-b deployment/service-c -n chain-reaction
```

### 2.2 Code to insert (STEP 2)

In **each** of `service_a.py`, `service_b.py`, and `service_c.py`, **replace** the commented block:

```python
# --- STEP 2: INSERT OTEL INSTRUMENTATION HERE ---
# (OTLPSpanExporter -> otel-collector:4317, FastAPIInstrumentor, RequestsInstrumentor, trace_id in logs)
```

with the following (adjust the logger so it includes `trace_id` as below).

**At the top of the file (after imports, before the FastAPI app):**

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

resource = Resource.create({"service.name": "service-a"})  # use "service-b" / "service-c" in B and C
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")))
trace.set_tracer_provider(provider)

FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()
# In service_c.py there are no outgoing HTTP calls; omit HTTPXClientInstrumentor there.
```

**The correlation key — inject `trace_id` into the JSON logger:**

Add a logging **Filter** that attaches the current span’s trace ID to every log record. Then your existing JsonFormatter will include it. Place this **after** the OTel setup and **before** the routes:

```python
def trace_id_filter(record):
    span = trace.get_current_span()
    ctx = span.get_span_context()
    record.trace_id = format(ctx.trace_id, "032x") if ctx.is_valid else ""
    return True

logger.addFilter(trace_id_filter)
```

Ensure your `JsonFormatter` includes extra attributes (e.g. by outputting all `record.__dict__` keys that are not standard logging fields). Then every `logger.info("...")` will automatically include `trace_id` in the JSON, and in Grafana you can query Loki by `trace_id="$__value"` when using Derived Fields from Tempo.

**Summary per file:**

- **service_a.py:** Set `service.name` to `"service-a"`, add FastAPIInstrumentor + HTTPXClientInstrumentor, and include `trace_id` in JSON logs.
- **service_b.py:** Same with `"service-b"`.
- **service_c.py:** Same with `"service-c"`, but **omit** HTTPXClientInstrumentor (no outbound HTTP).

OTel sends spans over **HTTP** to the Collector at `http://otel-collector:4318` (OTLP HTTP). The Collector forwards them to Tempo on 4317 (gRPC).

### 2.3 Redeploy and generate traffic again

After editing all three files and rebuilding:

```bash
docker build -t chain-reaction-app:latest ./app
kubectl rollout restart deployment/service-a deployment/service-b deployment/service-c -n chain-reaction
```

Repeat the port-forward and `curl` loop. Traces should appear in Tempo.

---

## Phase 3: The Discovery

**Goal:** Find the 2-second span in Tempo, identify Service-C as the culprit, and jump from a span to the corresponding logs in Loki using TraceID.

### 3.1 Find the waterfall trace

1. In Grafana, open **Explore** and select **Tempo**.
2. Search for traces (e.g. by service name or time range). Find a trace that shows a **~2 second** span.
3. Open the trace and view the **waterfall**. You will see:
   - **Service-A** (e.g. GET /) calling **Service-B** (/request),
   - **Service-B** calling **Service-C** (/request),
   - **Service-C** holding the request for ~2 seconds (simulated DB).

**Service-C is the culprit** for the latency.

### 3.2 Correlate with Loki (TraceID → logs)

1. In the Tempo trace view, copy the **TraceID** (or use the “View Logs” / “Derived Fields” flow if configured).
2. In **Explore**, select **Loki**.
3. Query by TraceID. If your logs include a `trace_id` field and Loki has an index or derived field for it, use:
   - `{namespace="chain-reaction"} | json | trace_id="<paste-trace-id>"`
   - Or set up a **Derived Field** in the Tempo data source: name `trace_id`, query in Loki `{namespace="chain-reaction"} | json | trace_id="$__value"`. Then “View Logs” from a span will open Loki with that TraceID.
4. You should see the JSON log lines for that exact request across A, B, and C — the **chain reaction** in one trace and one log view.

This is the payoff: metrics (e.g. latency), traces (waterfall), and logs (TraceID) tied together.

---

## Summary

| Phase | What you did |
|-------|----------------|
| **1. Blindness** | Deployed raw apps + Collector + Tempo + Loki (+ Promtail). Saw latency, zero traces. |
| **2. Instrumentation** | Added OTLPSpanExporter → Collector, FastAPIInstrumentor, RequestsInstrumentor, and trace_id in JSON logs. |
| **3. Discovery** | Found the 2s span in Tempo, identified Service-C, and used TraceID to open the same request in Loki. |

The **OTel Collector** is the standard way to receive, batch, and export telemetry at scale; your apps speak OTLP once, and the collector fans out to Tempo (and optionally other backends). Correlating traces and logs by TraceID is how platform and SRE teams debug request flows in production.
