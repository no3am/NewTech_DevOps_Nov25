# Prometheus Architecture Lab: The Pull Model

## Goal

Manually build the **Scrape Loop**. You will:

1. Deploy a Python app that **generates metrics** (the "patient").
2. Deploy a Prometheus server **configured to scrape (pull)** those metrics.

Prometheus uses a **Pull Model**: it periodically HTTP-GETs the metrics endpoint of each target. No push from the app—Prometheus is in control.

---

## Prerequisites

- **Minikube** (or another Kubernetes cluster) running.
- **kubectl** configured.
- **Docker** (used to build the app image).

---

## Part 1: Build the Image

The app lives in `app/`. We build it as `metric-app:v1` so the cluster can run it.

**1. Point your terminal at Minikube’s Docker daemon.**

Otherwise `docker build` would build on your host; Minikube would not see the image.

```bash
eval $(minikube docker-env)
```

or after you build the image 

`minikube image load metric-app:v1`

**2. Build the image.**

From the **prom** folder (parent of `app/`):

```bash
docker build -t metric-app:v1 ./app
```

You should see the image listed with:

```bash
docker images | grep metric-app
```

---

## Part 2: Deploy

Apply manifests in order so the ConfigMap exists before the Prometheus server.

**1. Deploy the app (Deployment + Service).**

```bash
kubectl apply -f k8s/1-app.yaml
```

**2. Deploy the Prometheus config (ConfigMap).**

```bash
kubectl apply -f k8s/2-prometheus-config.yaml
```

**3. Deploy the Prometheus server (Deployment + Service).**

```bash
kubectl apply -f k8s/3-prometheus-server.yaml
```

Wait until all Pods are ready:

```bash
kubectl get pods -w
```

(Ctrl+C to stop watching.)

---

## Part 3: Verify the Wiring

**1. Port-forward the Prometheus service.**

```bash
kubectl port-forward svc/prometheus-service 9090:9090
```

Leave this running in one terminal.

**2. Open Prometheus in your browser.**

Go to: **http://localhost:9090**

You should see the Prometheus UI.

---

## Part 4: The Test

**1. Check that the scrape target is UP.**

- In the UI: **Status → Targets**.
- Find the job **my-app-job**.
- The target **metric-app-service:8000** should be **GREEN (UP)**.

If it is UP, the scrape loop is working: Prometheus is pulling metrics from your app.

**2. Query a metric.**

- Go to **Graph** (or “Query”).
- In the query box, type: **http_requests_total** or **rate(http_requests_total[1m])**
- Click **Execute**.

You should see the counter (with labels like `status="200"` and `status="500"`) and/or the request rate.

**3. Watch the line go up.**

- Switch to the **Graph** tab.
- Leave the page open; the app keeps generating traffic (success and errors, varying latency).
- The line should **go up over time**. Then try the **PromQL Challenges** below.

---

## PromQL Challenges

The app now simulates a **messy web server**: it exposes a **Counter** (requests by status), a **Gauge** (in-progress requests), and a **Histogram** (request duration). Use these to practice PromQL.

### Why `rate()` for Counters but NOT for Gauges?

- **Counters** only go up. Prometheus stores the *cumulative* value. To get "how many per second" you must use **`rate()`** (or `irate()`): it computes the slope over a time window. So: **always use `rate(counter[window])`** when you care about throughput or error rate.
- **Gauges** are point-in-time values (current connections, free memory, in-progress requests). They go up and down. The scraped value *is* the value. Using **`rate()` on a gauge** is wrong—it would try to interpret the gauge as a monotonically increasing counter and give meaningless results. So: **query gauges directly**, no `rate()`.

Run each challenge in the Prometheus UI (**Graph** / query box), then click **Execute** and look at **Table** or **Graph**.

---

**Challenge 1 (Rate):** *"How many requests per second are we getting?"*

```promql
rate(http_requests_total[1m])
```

This is the request rate (all statuses) over the last 1 minute. Use **rate()** because `http_requests_total` is a Counter.

---

**Challenge 2 (Sum by):** *"What is our error rate vs success rate?"*

```promql
sum by (status) (rate(http_requests_total[1m]))
```

You get one line (or series) per `status` ("200" and "500"). Compare the two to see success vs failure rate.

---

**Challenge 3 (Gauges):** *"How many users are on the site right now?"*

```promql
in_progress_requests
```

**Do not use `rate()` here.** This is a Gauge—the value *is* the current number of in-progress requests. Query it as-is.

---

**Challenge 4 (The Boss Level — Histograms):** *"What is the 99th percentile latency? (How slow is the site for the unluckiest 1% of users?)"*

```promql
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

Prometheus stores histograms as counters per bucket (`_bucket`) and the special `le` (less-or-equal) label. **`histogram_quantile(0.99, ...)`** computes the 99th percentile from those buckets. Use a 5m window so the estimate is stable.

---

## Summary

| Component            | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **metric-app**       | Exposes `/metrics` on port 8000 (Counter, Gauge, Histogram).         |
| **prometheus-config** | Tells Prometheus *what* to scrape (my-app-job → metric-app-service:8000). |
| **Prometheus server** | Periodically pulls (scrapes) those metrics.                          |

This is the **Pull Model**: Prometheus discovers the target (via static_configs and the Service name) and scrapes it on an interval—no push from the app.
