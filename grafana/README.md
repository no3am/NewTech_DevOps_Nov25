# Grafana Lab: Prometheus + Grafana with Helm and Custom Metrics

## Scenario

You will use **Helm** to install the **kube-prometheus-stack** (Prometheus + Grafana + friends), explore the default infrastructure dashboards, deploy a **custom Python app** that exposes metrics, and build a **custom Grafana dashboard** to watch traffic in real time. The payoff: scale a load generator and watch the lines go **vertical** in Grafana.

---

## Prerequisites

- A Kubernetes cluster (e.g. Minikube) and **kubectl** configured.
- **Helm 3** installed.
- **Docker** (to build the custom app image).

---

## Step 1: The Helm Install

Add the Prometheus community Helm repo and install the full monitoring stack in the `monitoring` namespace:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
```

Wait until all Pods in `monitoring` are ready:

```bash
kubectl get pods -n monitoring -w
```

(Ctrl+C when everything is Running.)

You now have Prometheus, Grafana, Alertmanager, and the Prometheus Operator running. Prometheus is already scraping cluster metrics; we will add our **custom app** to that picture.

---

## Step 2: Access Grafana

Port-forward the Grafana service so you can open it in your browser:

```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```

Leave this running. Open **http://localhost:3000** in your browser.

**Log in:**

- **Username:** `admin`
- **Password:** `prom-operator`

*(If it doesn’t work, get the password from the cluster:*
`kubectl get secret -n monitoring monitoring-grafana -o jsonpath='{.data.admin-password}' | base64 -d`*.)*

---

## Step 3: The Cheat Code (Act 1)

Before we add our own app, see what **out-of-the-box** looks like.

1. In Grafana, go to **Dashboards** (left menu).
2. Open **Browse** and find the pre-installed **Kubernetes / Compute Resources / Namespace (Pods)** dashboard (or search for “Kubernetes”).
3. Select the **monitoring** namespace and a time range (e.g. Last 5 minutes).

You’re seeing **infrastructure metrics** that the stack is already collecting: CPU, memory, and pod usage. This is the “cheat code”: someone else built these dashboards; we’re about to build our own for **application** metrics.

---

## Step 4: Deploy the App (Act 2)

Our custom Flask app exposes `/` (Hello World), `/error` (returns 500), and `/metrics` for Prometheus. We need to build its image, then deploy it and a **ServiceMonitor** so Prometheus scrapes it.

**4a. Build and load the image**

From the **grafana** folder (parent of `app/`), point Docker at your cluster’s daemon (Minikube example), then build:

```bash
eval $(minikube docker-env)
docker build -t custom-api:v1 ./app
```

*(If you don’t use Minikube, push the image to a registry and update the image in `k8s/1-app.yaml`.)*

**4b. Deploy the app, ServiceMonitor, and load generator**

All of these resources go into the `monitoring` namespace so Prometheus (which watches that namespace) discovers our ServiceMonitor:

```bash
kubectl apply -f k8s/1-app.yaml
kubectl apply -f k8s/2-service-monitor.yaml
kubectl apply -f k8s/3-load-generator.yaml
```

- **1-app.yaml:** Deployment + Service for the Flask app. The Service has the label `app: custom-api` so the ServiceMonitor can find it.
- **2-service-monitor.yaml:** A **ServiceMonitor** that tells the Prometheus Operator to scrape `custom-api-service` on `/metrics`. That’s how our custom metric `http_requests_total` gets into Prometheus.
- **3-load-generator.yaml:** A Deployment that runs a loop calling your API every 2 seconds so there’s traffic to graph.

Check that the app and load generator are running:

```bash
kubectl get pods -n monitoring -l app=custom-api
kubectl get pods -n monitoring -l app=load-generator
```

Give Prometheus a minute to scrape; then we build the dashboard.

---

## Step 5: Build the Dashboard

Now we create a **custom dashboard** that shows request rate by HTTP status (200 vs 500) in real time.

1. In Grafana, click **+** (or **Create**) → **Dashboard**.
2. Click **Add visualization** (or **Add new panel**).
3. At the top, set the **Data source** to **Prometheus** (the one installed by the stack).
4. In the query editor, choose **PromQL** and enter:

   ```promql
   sum(rate(http_requests_total[1m])) by (http_status)
   ```

5. In the right-hand panel options, set a clear **Panel title** (e.g. “Request rate by status”).
6. Click **Apply** or **Save**. Save the dashboard with a name (e.g. “Custom API traffic”).

You should see (at least) two series: one for `http_status="200"` and one for `http_status="500"`. With one load-generator replica and a 2-second sleep, the lines will be relatively flat. Next, we make them **spike**.

---

## Step 6: The Spike (Act 3)


1. Keep your Grafana dashboard open on the panel you just created (with the PromQL query above). Use a short time range (e.g. **Last 5 minutes**) and refresh **Every 5s** if you like.
2. In a terminal, scale the load generator to **10 replicas**:

   ```bash
   kubectl scale deployment load-generator -n monitoring --replicas=10
   ```

3. **Tab back to Grafana** and watch the graph.

The lines should go **vertical**. You now have 10 pods hammering your API every 2 seconds; Prometheus is scraping the counter, and Grafana is plotting `rate(http_requests_total[1m])` by status. You’ve just connected **Helm → Prometheus → ServiceMonitor → custom app → Grafana** and seen the effect of load in real time.

When you’re done, scale back down (optional):

```bash
kubectl scale deployment load-generator -n monitoring --replicas=1
```

---

## Summary

| Step | What you did |
|------|----------------|
| **1** | Installed Prometheus + Grafana (and more) with Helm: `kube-prometheus-stack` in `monitoring`. |
| **2** | Opened Grafana via port-forward; logged in with `admin` / `prom-operator`. |
| **3** | Explored a pre-built **Kubernetes / Compute Resources / Namespace (Pods)** dashboard. |
| **4** | Deployed the custom Flask app, a **ServiceMonitor** so Prometheus scrapes it, and a **load generator**. |
| **5** | Built a dashboard with a Time Series panel and PromQL: `sum(rate(http_requests_total[1m])) by (http_status)`. |
| **6** | Scaled the load generator to 10 and watched the request rate **spike** in Grafana. |

You’ve gone from zero to a full monitoring stack with a custom instrumented app and a dashboard that reacts to load in real time.
