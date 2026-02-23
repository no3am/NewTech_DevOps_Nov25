# Mimir Lab: Prometheus → Mimir (Long-Term Storage via remoteWrite)

## Scenario

You already have the **kube-prometheus-stack** installed (Prometheus, Grafana, custom app, load generator). Now you add **Grafana Mimir** as a **long-term metrics store**: Prometheus will **push** (remote write) every scrape to Mimir, and you will **query Mimir** from Grafana. This is the same pattern Enterprise SREs use when a single Prometheus instance can’t hold all the data or when they need durable, queryable storage at scale.

---

## Prerequisites

- The **Grafana lab** completed: kube-prometheus-stack in the `monitoring` namespace, custom API and load generator running, and a dashboard (e.g. “Traffic Spike”) that shows `sum(rate(http_requests_total[1m])) by (http_status)` from **Prometheus**.
- **Helm 3** and **kubectl** configured.

---

## Step 1: The Warehouse

Deploy Mimir in **monolithic** mode so a single process runs all components (ingester, querier, compactor, etc.). That keeps CPU and memory low—ideal for labs and small clusters.

```bash
kubectl apply -f k8s/4-mimir.yaml
```

Wait for the Mimir pod to be ready:

```bash
kubectl get pods -n monitoring -l app=mimir -w
```

(Ctrl+C when the pod is **Running** and ready.)

You now have **mimir-service** on port **8080** in the `monitoring` namespace. It’s not receiving data yet; Prometheus will be configured to push to it in the next step.

---

## Step 2: The Pipeline (Helm Upgrade)

Tell Prometheus to **remote write** every scrape to Mimir. You do this by **upgrading** the existing Helm release with a values file that sets `prometheus.prometheusSpec.remoteWrite`.

From the **Mimir** folder (where `k8s/5-prometheus-values.yaml` lives):

```bash
helm upgrade monitoring prometheus-community/kube-prometheus-stack -f k8s/5-prometheus-values.yaml -n monitoring
```

This **upgrade** does not reinstall everything; it only applies the new Prometheus config. Prometheus will **immediately** start shipping scraped metrics to **http://mimir-service:8080/api/v1/push**. No need to restart the app or the load generator—data flows into Mimir in the background.

---

## Step 3: The Connection

Add Mimir as a **Prometheus-type data source** in Grafana so you can query Mimir instead of (or in addition to) Prometheus.

1. Open **Grafana** (e.g. `kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80` and go to http://localhost:3000).
2. Go to **Connections** → **Data sources** (or **Configuration** → **Data Sources**).
3. Click **Add data source** and choose **Prometheus**.
4. Configure:
   - **Name:** `Mimir`
   - **URL:** `http://mimir-service:8080/prometheus`  
     *(Mimir exposes a Prometheus-compatible query API at this path.)*
   - Turn **off** **Alerting** for this data source (we’re only querying).
5. Click **Save & test**. You should see “Data source is working.”

You now have two data sources: the original **Prometheus** (short-term, local) and **Mimir** (where Prometheus is continuously pushing data). The same PromQL works against both.

---

## Step 4: The Proof

Prove that the pipeline is end-to-end: the same metrics you see from Prometheus should appear when you query **Mimir**.

1. Open the **“Traffic Spike”** (or custom API traffic) dashboard from the previous Grafana lab.
2. **Edit** one of the panels that uses `sum(rate(http_requests_total[1m])) by (http_status)` (or similar).
3. In the panel editor, change the **Data source** from **Prometheus** to **Mimir**.
4. Save the panel (and the dashboard if prompted).

The graph should look **the same** (or very close): the data is now coming from Mimir. Prometheus wrote it there via remote write; you’re reading it back via Mimir’s Prometheus-compatible API. That’s the full loop: **scrape → remote write → query**.

---

## Summary

| Step | What you did |
|------|----------------|
| **1** | Deployed Mimir (monolithic) with `k8s/4-mimir.yaml` and waited for the pod. |
| **2** | Upgraded the stack with `k8s/5-prometheus-values.yaml` so Prometheus **remote writes** to Mimir. |
| **3** | Added a **Mimir** data source in Grafana (URL: `http://mimir-service:8080/prometheus`, Alerting off). |
| **4** | Switched a dashboard panel to the **Mimir** data source and confirmed the same metrics. |

You’ve connected Prometheus to Mimir for long-term storage and queried it from Grafana—the same pattern used when a cluster outgrows a single Prometheus or when teams centralize metrics in a dedicated store.
