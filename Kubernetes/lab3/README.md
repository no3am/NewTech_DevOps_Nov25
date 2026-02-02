# Kubernetes Lab 3: Services (ClusterIP vs NodePort)

## Objective

Learn how **Kubernetes Services** work and how they **load balance** traffic across multiple Pods. You will hit **one URL** and get responses from **3 different Pods**, proving that the Service distributes requests.

---

## What You'll See

When you refresh the page **10 times**, the **Pod name** on the screen will change randomly:

- **Request 1:** `Request served by Pod: whoami-7d8f9c-xyz12`
- **Request 2:** `Request served by Pod: whoami-7d8f9c-abc34`
- **Request 3:** `Request served by Pod: whoami-7d8f9c-def56`
- **Request 4:** Back to a previous Pod... and so on.

This proves the **Service is load balancing** across your 3 replicas.

---

## Prerequisites

- **Minikube** installed and running
- **kubectl** installed
- **Docker** (for building the image)

---

## Step 1: Build the Image

Build the `whoami` image locally:

```bash
docker build -t whoami:latest .
```

### Minikube trick: Make the image available inside Minikube

Minikube has its **own Docker daemon**. Your local `whoami:latest` image is not visible inside Minikube by default. Use **one** of these options:

**Option A – Load the image into Minikube (recommended):**

```bash
minikube image load whoami:latest
```

**Option B – Use Minikube's Docker daemon for builds:**

```bash
eval $(minikube docker-env)
docker build -t whoami:latest .
```

After this, `whoami:latest` is available to Pods running in Minikube.

---

## Step 2: Apply the Deployment

Create the **whoami** Deployment (3 replicas):

```bash
kubectl apply -f k8s/1-deployment.yaml
```

Verify Pods are running:

```bash
kubectl get pods -l app=whoami
```

You should see **3 Pods** in `Running` state.

---

## Step 3: Apply the Services

**ClusterIP** (internal only – optional, for understanding):

```bash
kubectl apply -f k8s/2-service-clusterip.yaml
```

**NodePort** (accessible from your machine – **this is what you'll test**):

```bash
kubectl apply -f k8s/3-service-nodeport.yaml
```

Verify the Service:

```bash
kubectl get svc whoami-external
```

You should see `whoami-external` with type **NodePort** and port **30007**.

---

## Step 4: The Test – Prove Load Balancing

**One URL, multiple Pods.** Refresh 10 times and watch the Pod name change.

### Get the URL

**Minikube:**

```bash
minikube service whoami-external --url
```

Use the URL shown (e.g. `http://192.168.49.2:30007`).

### Option A: Browser

1. Open the URL in your browser.
2. **Refresh 10 times.**
3. The line **"Request served by Pod: …"** should show **different Pod names** (e.g. `whoami-xyz` → `whoami-abc` → `whoami-def`).

### Option B: curl

```bash
for i in {1..10}; do
  echo "Request $i:"
  curl http://$(minikube ip):30007
  echo ""
done
```

---

## Expected Output

You should see the **Pod name change** as you hit the Service multiple times:

```
Request served by Pod: whoami-7d8f9c-xyz12

Request served by Pod: whoami-7d8f9c-abc34

Request served by Pod: whoami-7d8f9c-def56

Request served by Pod: whoami-7d8f9c-xyz12
...
```

This demonstrates that the **Service is load balancing** requests across the 3 Pods.

---

## ClusterIP vs NodePort

| Type       | Name             | Use case                          | Access                          |
|-----------|------------------|------------------------------------|----------------------------------|
| **ClusterIP** | whoami-internal  | Internal traffic inside the cluster | Only from other Pods in the cluster |
| **NodePort**  | whoami-external  | External access for testing        | From your machine via `<NodeIP>:30007` |

- **ClusterIP:** Port 80 → TargetPort 5000. No NodePort. Not reachable from outside the cluster.
- **NodePort:** Port 80 → TargetPort 5000, **NodePort 30007**. Reachable at `<minikube ip>:30007`.

---

## Cleanup

```bash
kubectl delete -f k8s/3-service-nodeport.yaml
kubectl delete -f k8s/2-service-clusterip.yaml
kubectl delete -f k8s/1-deployment.yaml
```

---

## Key Takeaway

**One URL → Service → Load balanced across 3 Pods.** The Service forwards each request to one of the Pods (e.g. round-robin). That’s why the Pod name changes on each refresh.
