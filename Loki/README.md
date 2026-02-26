# The Poison Pill — Correlate Prometheus Metrics with Loki Logs in Grafana

## Goal

Learn to **correlate metrics and logs**: use **Prometheus** to see *that* something is wrong (error rate spikes), then use **Loki** to see *why* (the exact JSON log lines). The victim is a "Payment Processor" app; a hidden **poison pill** (`item=cursed_amulet`) triggers 500 errors. You will find it by joining metrics and logs in Grafana Explore.

---

## Prerequisites

- A Kubernetes cluster and **kubectl** configured.
- **Helm 3** installed.

---

## Step 1: Install the Observability Stack

Install **kube-prometheus-stack** (Prometheus + Grafana) and **loki-stack** (Loki + Promtail) in the `monitoring` namespace so Grafana can reach both.

**Add repos and install Prometheus stack:**

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
```

Wait for Pods to be ready:

```bash
kubectl get pods -n monitoring -w
```

**Install Loki stack (use release name `loki` so the service is `loki`):**

```bash
helm install loki grafana/loki-stack --namespace monitoring
```

You may see **"This chart is deprecated"** — the install still works for this lab. The **"SessionAffinity is ignored for headless services"** messages are harmless and can be ignored. For new production use, Grafana recommends the unified **grafana/loki** chart (single-binary or distributed) and **Grafana Alloy** for log collection instead of Promtail.

Wait for Loki and Promtail to be ready. Promtail will collect logs from cluster Pods and send them to Loki. Check pods by release label (release name was `loki`):

```bash
kubectl get pods -n monitoring -l "app.kubernetes.io/instance=loki"
```

If that shows no resources, list all pods in the namespace and look for names containing `loki` or `promtail`:

```bash
kubectl get pods -n monitoring
helm list -n monitoring
```

You should see at least a Loki pod (e.g. `loki-0` or `loki-loki-...`) and a Promtail DaemonSet (e.g. `loki-promtail-...`). If no Loki-related pods exist, the chart may have failed to install; run `helm status loki -n monitoring` for details.

---

## Step 2: Deploy the App and Traffic

Build the Payment Processor image (from the **Loki** folder, with Docker pointed at your cluster if using Minikube):

```bash
eval $(minikube docker-env)
docker build -t payment-processor:v1 ./app
```

or after you build the image 

`minikube image load payment-processor:v1`

Apply the manifests to deploy the app, the ServiceMonitor, and the traffic generator:

```bash
kubectl apply -f k8s/
```

This creates:

- **payment-processor** Deployment and Service (label `app: payment-processor`) — the victim app.
- **ServiceMonitor** so Prometheus scrapes `/metrics` from the app.
- **traffic-generator** — a loop that calls `/checkout` about once per second, with ~90% normal items (`shoes`, `hat`) and ~10% **cursed_amulet** (the poison pill that returns 500).

Verify:

```bash
kubectl get pods -n monitoring -l app=payment-processor
kubectl get pods -n monitoring -l app=traffic-generator
```

---

## Step 3: Open Grafana and Log In

Port-forward Grafana:

```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```

Open **http://localhost:3000** in your browser.

- **Username:** `admin`
- **Password:** `prom-operator` (or read from the cluster:  
  `JmT5MQDu2NbDjMJ8ZhoifYjlkLi8FW0WUd8fyqbT`)

---

## Step 4: Add Loki as a Data Source

1. Go to **Connections** → **Data sources** (or **Configuration** → **Data sources**).
2. Click **Add data source** and choose **Loki**.
3. Configure:
   - **URL:** `http://loki.monitoring.svc.cluster.local:3100`  
     **Must start with `http://`** — if the URL has no scheme, queries will fail with “unsupported protocol scheme ""”.
   - **Access:** set to **Server (default)**.  
     If this is **Browser**, Grafana will try to reach Loki from your machine; the in-cluster hostname won’t resolve and you’ll get “Unable to connect.” **Server** makes the Grafana pod (in the cluster) call Loki, so the URL works.
4. Click **Save & test**.  
   - If you see “Data source is working,” you’re done.  
   - If you see “Unable to connect with Loki,” see the note below — the datasource may still be saved and work.

**If “Save & test” shows “Unable to connect with Loki”** and Grafana logs show:
`Loki health check failed ... parse error at line 1, col 1: syntax error: unexpected IDENTIFIER`  
then Grafana’s health check is sending a query that Loki’s parser rejects (a known compatibility quirk). **Workaround:** The datasource is usually **saved anyway**. Ignore the error, go to **Explore**, choose the Loki datasource, and run e.g. `{namespace="monitoring"}` or `{app="payment-processor"}` — if you see logs, the connection works and you can ignore the failed health check.

**If you see a different error:**  
- Confirm **Access** is **Server**, not Browser.  
- Check Grafana logs: `kubectl logs -n monitoring deployment/monitoring-grafana -c grafana --tail=100`.  
- Test Loki’s API from the cluster:  
  `kubectl run -n monitoring curl --rm -it --restart=Never --image=curlimages/curl -- curl -s "http://loki.monitoring.svc.cluster.local:3100/loki/api/v1/labels"`  
  (should return JSON with `"values": [...]`).

**If queries fail with “unsupported protocol scheme ""”:**  
The datasource URL is empty or missing `http://`. Edit the Loki data source and set **URL** to **`http://loki.monitoring.svc.cluster.local:3100`** (including `http://`), then save.

You now have **Prometheus** (metrics) and **Loki** (logs) available in Grafana.

**If Explore shows “An error occurred within the plugin” when you select Loki:**  
This often happens with the same compatibility issue (newer Grafana sending requests that Loki 2.9 from loki-stack rejects). Try in order:

1. **Reproduce and check the real error:** Open Explore, select Loki, then run:  
   `kubectl logs -n monitoring deployment/monitoring-grafana -c grafana --tail=50`  
   Look for lines mentioning `loki` or `tsdb.loki` and the error message.

2. **Use Code mode and run a query:** In the Loki query area, switch the editor to **Code** (not Builder). Type a simple query like `{namespace="monitoring"}` and click **Run query**. Sometimes the plugin only fails when loading the label browser; a manual query may still work.

3. **If the error appears as soon as you select Loki** (before you can type), the plugin is failing on load (e.g. when fetching labels). Then use **provisioned Loki** so it’s loaded with the same path as other datasources: see **Troubleshooting: Provision Loki via Helm** at the end of this README.

---

## Step 5: The Investigation — Correlate Metrics and Logs

Use **Explore** in **split view** to see the error spike in Prometheus and the matching error logs in Loki.

1. In the left menu, open **Explore**.
2. Use **split view** (split-screen icon or “Split” option) so you have **two panels** side by side.

**Left panel — Prometheus (the “that something is wrong”):**

- Select data source **Prometheus**.
- In the query box, run:

  ```promql
  sum(rate(http_requests_total{status="500"}[1m]))
  ```

- Click **Run query**.

You should see **spikes** in the 500 error rate. The traffic generator sends `cursed_amulet` about 10% of the time, so the rate will jump periodically.

**If the Prometheus query returns nothing:** Ensure the payment-processor and traffic-generator are running (`kubectl get pods -n monitoring -l app=payment-processor`). The ServiceMonitor must have the label **`release: monitoring`** so Prometheus discovers it — re-apply `k8s/2-service-monitor.yaml` (the file was updated to add this label). Wait a minute for a scrape, then try the query again; you can also try `http_requests_total` or set time range to **Last 15 minutes**.

**Right panel — Loki (the “why”):**

- Select data source **Loki**.
- In the query box, run:

  ```logql
  {app="payment-processor"} | json | level="error"
  ```

  If that returns no logs, Promtail from loki-stack often doesn’t add `app` as a stream label. Use **namespace** and filter by the payment-processor’s unique JSON field:

  ```logql
  {namespace="monitoring"} |= "ERR-999"
  ```

  or `{namespace="monitoring"} |= "cursed_amulet"`. These use a **line filter** (match the raw log line); they don’t rely on `| json` label filters, which can fail to match in some Loki versions. Only the payment-processor logs those strings.

- Click **Run query**.

You should see **log lines** that appear when the spikes happen. Each line is a JSON log from the app. Open a few: you will see `"item": "cursed_amulet"` and `"error_code": "ERR-999"`. That’s the poison pill — the exact request that triggers the 500s.

**What `| json` does in LogQL:**  
The app logs in **JSON** to stdout. `| json` in LogQL **parses** each log line as JSON and extracts fields as labels. Then `level="error"` filters to lines where the parsed `level` field equals `"error"`. So you go from raw JSON lines to structured filtering and can correlate by time with the Prometheus panel.

**If you see “Failed to load log volume for this query” (and a parse error) at the top:** That comes from Grafana’s log volume histogram; it uses a query that Loki 2.9 rejects. **Ignore it** — the log lines at the bottom are correct and are what you need for the lab.

---

## Troubleshooting: “An error occurred within the plugin” in Explore

If selecting Loki in Explore immediately shows “An error occurred within the plugin” (and **Code** mode + a manual query doesn’t help), the Loki plugin in your Grafana version is likely sending requests that **loki-stack** (Loki 2.9) rejects. Two options:

### Option A: Provision Loki via Helm (pre-configured datasource)

Add Loki as an **additional datasource** when installing or upgrading the kube-prometheus-stack so Grafana loads it at startup:

```bash
helm upgrade monitoring prometheus-community/kube-prometheus-stack -n monitoring \
  --reuse-values \
  -f - <<'EOF'
grafana:
  additionalDataSources:
    - name: Loki
      type: loki
      access: proxy
      url: http://loki.monitoring.svc.cluster.local:3100
      isDefault: false
EOF
```

Then restart or wait for Grafana to reload. Try Explore again. If the plugin still errors on load, use Option B.

### Option B: Use the newer Loki chart (better compatibility)

Replace **loki-stack** with the non-deprecated **grafana/loki** chart in single-binary mode so Loki matches newer Grafana:

1. **Uninstall loki-stack** (this removes Loki and Promtail; we will re-add Loki only):
   ```bash
   helm uninstall loki -n monitoring
   ```

2. **Install the unified Loki chart** (single binary, no Promtail in this example; you’d need a log collector like Alloy or Promtail separately for the payment-processor logs):
   ```bash
   helm repo add grafana https://grafana.github.io/helm-charts
   helm repo update
   helm install loki grafana/loki -n monitoring \
     --set "loki.auth_enabled=false" \
     --set "singleBinary.replicas=1" \
     --set "loki.commonConfig.replication_factor=1"
   ```

3. **Add the Loki data source again** in Grafana (URL `http://loki.monitoring.svc.cluster.local:3100`, Access: **Server**).  
   For the Poison Pill lab you still need logs from the payment-processor pods; the loki-stack chart included Promtail. With the Loki-only chart you must install **Promtail** or **Grafana Alloy** separately and point it at Loki if you want to repeat the full log correlation. For a quick check that Explore works, you can query `{namespace="monitoring"}` once some logs exist.

---

## Summary

| Step | What you did |
|------|----------------|
| **1** | Installed **kube-prometheus-stack** and **loki-stack** (release name `loki`) in `monitoring`. |
| **2** | Built the Payment Processor image and applied **k8s/** (app, ServiceMonitor, traffic generator). |
| **3** | Port-forwarded Grafana and logged in. |
| **4** | Added **Loki** as a data source with URL **http://loki:3100**. |
| **5** | In **Explore** (split view): **Prometheus** — `sum(rate(http_requests_total{status="500"}[1m]))` for error spikes; **Loki** — `{app="payment-processor"} | json | level="error"` to see the cursed_amulet error logs. |

You used **metrics** to detect the problem and **logs** to identify the exact failing request — the same workflow SREs use in production.
