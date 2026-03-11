# The Chain Reaction — Capstone Lab

## Mission Brief

You will instrument a **3-tier microservice architecture** with **OpenTelemetry (OTel)**, route traces through an **OTel Collector** to **Grafana Tempo**, and correlate them with **Loki** logs. This is the standard pattern for production observability: one collector, one protocol (OTLP), and trace–log correlation in Grafana.

**The stack:**

- **Service-A** (Gateway) → **Service-B** (Logic) → **Service-C** (Database). Service-C simulates a 2-second “database” call.
- **OTel Collector**: receives OTLP from the apps, batches, and exports to Tempo.
- **Tempo**: stores traces. **Loki**: stores logs. **Grafana**: queries both and links trace ↔ logs via TraceID.

---

## Prerequisites

- Kubernetes cluster (e.g. **Minikube**), **kubectl**, **Docker** (or similar).
- The lab is **self-contained**: you deploy Grafana, Tempo, and Loki in the same namespace. No existing Grafana or other stacks are required.

---

## Phase 1: The Blindness

**Goal:** Deploy the raw apps and the observability backend. See latency but **zero traces** in Tempo.

### 1.1 Create namespace and infrastructure

```bash
kubectl apply -f k8s/0-otel-collector.yaml
kubectl apply -f k8s/1-tempo.yaml
kubectl apply -f k8s/2-loki.yaml
kubectl apply -f k8s/4-promtail.yaml
kubectl apply -f k8s/5-grafana.yaml
```

Wait until Pods are ready in `chain-reaction` (grafana, tempo, loki, otel-collector, promtail).

### 1.2 Build and deploy the apps (no tracing yet)

From the **ChainReaction** folder:

```bash
eval $(minikube docker-env)
docker build -t chain-reaction-app:latest ./app
kubectl apply -f k8s/3-apps.yaml
```

### 1.3 Expose Service-A and generate traffic

```bash
kubectl port-forward -n chain-reaction svc/service-a 8000:8000
# In another terminal:
while true; do curl -s http://localhost:8000/; sleep 1; done
```

You will see ~2 second latency (A → B → C; C sleeps 2s).

### 1.4 Open Grafana and add Tempo and Loki

```bash
kubectl port-forward -n chain-reaction svc/grafana 3000:3000
```

Open **http://localhost:3000**. Log in with **admin** / **admin**.

Add data sources (Connections → Data sources → Add data source):

- **Tempo:** Type Tempo, URL **`http://tempo:3200`**, Access: Server. Save & test.
- **Loki:** Type Loki, URL **`http://loki:3100`**, Access: Server. Save & test.

### 1.5 Observe the blindness

In Grafana **Explore**, select **Tempo** and run a search. You will see **no traces** — the apps are not instrumented yet.

---

## Phase 2: The Instrumentation

**Goal:** Add OTel to each service so traces flow to Tempo and logs carry `trace_id` for correlation.

### 2.1 Dependencies

Add to `app/requirements.txt`:

```
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-http
opentelemetry-instrumentation-fastapi
opentelemetry-instrumentation-httpx
```

### 2.2 Instrumentation and trace_id in logs

In **each** of `service_a.py`, `service_b.py`, and `service_c.py`:

1. **OTel setup** (after creating the FastAPI app and logger): TracerProvider, BatchSpanProcessor with `OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")`, `FastAPIInstrumentor.instrument_app(app)`, and in A and B only `HTTPXClientInstrumentor().instrument()`. Use `Resource.create({"service.name": "service-a"})` (or `service-b` / `service-c`).

2. **Correlation key:** Add a logging Filter that sets `record.trace_id` from the current span context (32-char hex), then `logger.addFilter(trace_id_filter)`. Your JsonFormatter will then include `trace_id` in every log line.

The app code in this repo already includes this; if you are following the lab from scratch, replace the `# --- STEP 2: INSERT OTEL INSTRUMENTATION HERE ---` block with the OTel setup and the trace_id filter.

### 2.3 Rebuild and redeploy

```bash
eval $(minikube docker-env)
docker build -t chain-reaction-app:latest ./app
kubectl rollout restart deployment/service-a deployment/service-b deployment/service-c -n chain-reaction
```

Repeat the port-forward and `curl` loop. Traces should appear in Tempo.

---

## Phase 3: The Discovery

**Goal:** Find the 2-second span in Tempo, identify Service-C as the culprit, and jump from a trace to logs in Loki via TraceID.

### 3.1 Find the waterfall trace

1. In Grafana **Explore**, select **Tempo**.
2. Choose **TraceQL** as the query type and run:
   ```text
   { resource.service.name = "service-a" }
   ```
   Set time range to **Last 5 minutes** (and ensure traffic is running).
3. Open a trace to view the **waterfall**: Service-A → Service-B → Service-C, with Service-C holding the request ~2 seconds.

**Service-C is the culprit** for the latency.

### 3.2 Correlate with Loki (TraceID → logs)

1. In the Tempo trace view, copy the **TraceID**.
2. In **Explore**, select **Loki**.
3. Run:
   ```text
   {namespace="chain-reaction"} | json | trace_id="<paste-trace-id>"
   ```
   Use the TraceID as **32 lowercase hex characters** (no spaces or dashes). Set time range to include when you generated the request.
4. You should see the JSON log lines for that request across A, B, and C — the **chain reaction** in one trace and one log view.

---

## Summary

| Phase | What you did |
|-------|----------------|
| **1. Blindness** | Deployed raw apps + Collector + Tempo + Loki + Promtail. Saw latency, zero traces. |
| **2. Instrumentation** | Added OTel (OTLPSpanExporter → Collector, FastAPIInstrumentor, HTTPXClientInstrumentor) and trace_id in JSON logs. |
| **3. Discovery** | Found the 2s span in Tempo, identified Service-C, and used TraceID to open the same request in Loki. |

The **OTel Collector** is the standard way to receive, batch, and export telemetry; your apps speak OTLP once, and the collector forwards to Tempo. Correlating traces and logs by TraceID is how teams debug request flows in production.

---

## Troubleshooting

- **Tempo returns 400:** Use **TraceQL** (not the Search tab). Query: `{ resource.service.name = "service-a" }`.
- **No traces (0 series):** Rebuild with `eval $(minikube docker-env)` so the cluster uses the new image, then restart the three app deployments. Ensure the port-forward and `curl` loop are running and time range is Last 5 minutes.
- **Loki "too many unhealthy instances in the ring":** Loki is configured with `replication_factor: 1`. Re-apply `k8s/2-loki.yaml` and restart the Loki deployment.
- **No logs in Loki:** Re-apply `k8s/4-promtail.yaml` and restart the Promtail DaemonSet. Wait 1–2 minutes, generate traffic, then query `{namespace="chain-reaction"}`. Use trace_id as 32-character lowercase hex from Tempo.
- **`minikube ssh "ls /var/log/pods"` is empty:** On Minikube Docker driver the node often has no `/var/log/pods`, so Promtail has nothing to scrape. Workaround: run this lab in the **same namespace as your Loki lab** (e.g. `monitoring`). Deploy the ChainReaction stack and apps into that namespace so the existing Promtail from the Loki lab picks up the app logs; query Loki with that namespace (e.g. `{namespace="monitoring"}`).
