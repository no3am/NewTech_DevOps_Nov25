# Kubernetes Lab 6: StatefulSets

## Objective

Deploy a **stateful** Nginx service to see how Kubernetes gives Pods:

- **Ordered, graceful** deployment and scaling
- **Stable network identities** (DNS names that don’t change)
- **Persistent storage** that stays bound to a specific Pod (sticky volumes)

This is important for databases, queues, and any workload that needs a stable identity and durable storage per replica.

---

## Prerequisites

- A Kubernetes cluster (v1.20+) with a **default StorageClass** (e.g. Minikube, kind, or cloud provider)
- `kubectl` installed and configured

---

## The Exercise

### 1. Headless Service (`nginx-service.yaml`)

StatefulSets need a **Headless Service** so that:

- The control plane can track and manage the Pods
- Each Pod gets a stable DNS name: `<pod-name>.<service-name>.<namespace>.svc.cluster.local`

**Headless** means `clusterIP: None`: no single Cluster IP. DNS returns the **individual Pod IPs**, so clients can reach `web-0`, `web-1`, `web-2` by name.

### 2. StatefulSet (`nginx-statefulset.yaml`)

The StatefulSet defines:

- **3 replicas** of Nginx
- **volumeClaimTemplate**: each Pod gets its **own** 1Gi PVC (e.g. `www-web-0`, `www-web-1`, `www-web-2`)
- **Stable names**: Pods are named `web-0`, `web-1`, `web-2` and keep those names and their volumes for their lifetime

---

## Deployment

Apply both manifests:

```bash
kubectl apply -f k8s/nginx-service.yaml -f k8s/nginx-statefulset.yaml
```

---

## Verification

### 1. Pod creation order

Pods are created **one by one**, in order (0, then 1, then 2):

```bash
kubectl get pods -w -l app=nginx
```

You should see `web-0` become Running, then `web-1`, then `web-2`. This is **ordered, graceful** rollout.

### 2. Stable hostnames

Each Pod has a **unique, stable** hostname that matches its name:

```bash
for i in 0 1 2; do kubectl exec web-$i -- hostname; done
```

Expected output:

```
web-0
web-1
web-2
```

### 3. Stable DNS

From another Pod in the cluster you can resolve:

- `web-0.nginx`
- `web-1.nginx`
- `web-2.nginx`

These names are stable even if a Pod is rescheduled.

### 4. One PV per Pod (sticky storage)

Each replica has its **own** PVC, created from the `volumeClaimTemplate`:

```bash
kubectl get pvc -l app=nginx
```

You should see three PVCs (e.g. `www-web-0`, `www-web-1`, `www-web-2`), each bound to a PV. Storage is **sticky**: when `web-1` is recreated, it gets the same PVC and the same data.

---

## Summary

| Feature            | StatefulSet behavior |
|--------------------|----------------------|
| **Ordering**       | Pods created/updated in order (0 → 1 → 2) |
| **Stable identity** | Fixed names and hostnames (web-0, web-1, web-2) |
| **Stable DNS**     | Headless Service gives each Pod a stable DNS name |
| **Sticky storage** | Each Pod has its own PVC from the volumeClaimTemplate |

---

## Cleanup

```bash
kubectl delete -f k8s/nginx-statefulset.yaml -f k8s/nginx-service.yaml
kubectl get pvc   # Delete any remaining PVCs if needed: kubectl delete pvc -l app=nginx
```
