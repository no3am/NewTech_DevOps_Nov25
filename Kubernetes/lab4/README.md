# Kubernetes Lab 4: ConfigMaps and Secrets

## Objective

Learn how to inject **configuration** (ConfigMaps) and **sensitive data** (Secrets) into Pods. We'll build a **Top Secret** dashboard for a spy agency that shows a mission name (public) and an access code (classified).

---

## The Scenario

- **Mission Name** → Public knowledge → **ConfigMap**
- **Access Code** → Classified → **Secret**

The app reads two environment variables: `MISSION_NAME` and `ACCESS_CODE`. You'll see how to feed them from a ConfigMap and a Secret using `valueFrom`.

---

## Prerequisites

- Minikube running
- kubectl installed
- Docker (for building the image)

---

## Step 1: Build the Image

```bash
docker build -t top-secret-dashboard:latest .
```

**Minikube users** – make the image available inside the cluster:

```bash
minikube image load top-secret-dashboard:latest
```

---

## Step 2: Apply the ConfigMap and Secret **First**

Apply the ConfigMap and Secret **before** the Deployment:

```bash
kubectl apply -f k8s/1-configmap.yaml
kubectl apply -f k8s/2-secret.yaml
```

**Why first?** The Deployment’s Pod template references these objects by name (`spy-config` and `spy-secret`). When the Pod starts, Kubernetes injects the env vars from them. If the ConfigMap or Secret don’t exist, the Pod can’t resolve `configMapKeyRef` / `secretKeyRef` and may fail to start or stay in a bad state. So create the config and secret first, then the workload.

---

## Step 3: Apply the Deployment (and Service)

```bash
kubectl apply -f k8s/3-deployment.yaml
```

Wait for the Pod to be ready:

```bash
kubectl get pods -l app=top-secret-dashboard
```

Get the URL (Minikube):

```bash
minikube service top-secret-dashboard --url
```

Or open in browser:

```bash
minikube service top-secret-dashboard
```

You should see something like:

**Mission: Operation Golden Eye**  
**Secret Code: 007**

---

## Step 4: The Experiment – ConfigMaps Don’t Update Running Pods

This shows that **env vars are set only when the Pod is created**. Changing a ConfigMap does **not** update already-running Pods.

### 4.1 Change the mission in the ConfigMap

Edit `k8s/1-configmap.yaml` and change the mission to **Operation Skyfall**:

```yaml
data:
  mission: "Operation Skyfall"
```

### 4.2 Apply the updated ConfigMap

```bash
kubectl apply -f k8s/1-configmap.yaml
```

### 4.3 Refresh the browser

**Question:** Did the page change to "Operation Skyfall"?

**Answer:** No. **Pods do not automatically pick up changes to ConfigMaps or Secrets.** The environment variables were set when the Pod was created. Updating the ConfigMap only affects **new** Pods.

### 4.4 Force a new Pod (so it reads the new ConfigMap)

Delete the Pod so the Deployment creates a new one:

```bash
kubectl get pods -l app=top-secret-dashboard
# Copy the Pod name, then:
kubectl delete pod <pod-name>
```

Or in one go:

```bash
kubectl delete pod -l app=top-secret-dashboard
```

Wait a few seconds for the new Pod to be ready, then **refresh the browser again**.

**Now** you should see **Mission: Operation Skyfall** and **Secret Code: 007**.

**Takeaway:** To pick up ConfigMap/Secret changes, you need a **new** Pod (e.g. delete the Pod, or rollout a new Deployment version).

---

## Summary

| Resource    | Use for              | In this lab          |
|------------|----------------------|----------------------|
| **ConfigMap** | Non-sensitive config | Mission name         |
| **Secret**    | Sensitive data       | Access code (base64) |

- **ConfigMap** `spy-config`: key `mission` → env var `MISSION_NAME`.
- **Secret** `spy-secret`: key `code` (base64 `007` → `MDA3`) → env var `ACCESS_CODE`.
- Deployment uses `valueFrom` with `configMapKeyRef` and `secretKeyRef` to inject them. No config or secrets hardcoded in the image.

---

## Cleanup

```bash
kubectl delete -f k8s/3-deployment.yaml
kubectl delete -f k8s/2-secret.yaml
kubectl delete -f k8s/1-configmap.yaml
```
