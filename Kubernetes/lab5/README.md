# Kubernetes Lab 5: Persistent Volumes (PVCs)

## Objective

Prove that **without a Volume**, database data is **lost** when a Pod is recreated — and **with a PVC**, data **survives**. We use Postgres: no volume = ephemeral data; PVC = persistent data.

---

## Prerequisites

- Minikube (or any Kubernetes cluster with a default StorageClass for dynamic provisioning)
- kubectl

---

## Part 1: The Fail (No Volume = Data Lost)

### 1.1 Deploy Postgres **without** a volume

```bash
kubectl apply -f k8s/1-postgres-stateless.yaml
```

Wait for the Pod to be Ready:

```bash
kubectl get pods -l app=postgres-stateless
```

### 1.2 Create data inside the Pod

Exec into the Postgres Pod and create a table and insert a row:

```bash
kubectl exec -it $(kubectl get pod -l app=postgres-stateless -o jsonpath='{.items[0].metadata.name}') -- psql -U labuser -d labdb -c "
CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT);
INSERT INTO users (name) VALUES ('Alice');
SELECT * FROM users;
"
```

You should see **Alice** in the output.

### 1.3 Delete the Pod

**WARNING: DELETING POD NOW.** This simulates a crash or node failure. Without a volume, all data in the container is gone.

```bash
kubectl delete pod -l app=postgres-stateless
```

Wait for the **new** Pod to be Running (the Deployment will create a replacement):

```bash
kubectl get pods -l app=postgres-stateless -w
# Ctrl+C when Running
```

### 1.4 Check for Alice

```bash
kubectl exec -it $(kubectl get pod -l app=postgres-stateless -o jsonpath='{.items[0].metadata.name}') -- psql -U labuser -d labdb -c "SELECT * FROM users;"
```

**Result:** The table `users` is **gone**. Alice is **gone**. Data was stored only on the container filesystem; when the Pod was deleted, that filesystem was destroyed.

---

## Part 2: The Fix (With PVC = Data Survives)

### 2.1 Remove the stateless deployment (optional, to avoid port conflicts)

```bash
kubectl delete -f k8s/1-postgres-stateless.yaml
```

### 2.2 Create the PVC and deploy Postgres **with** the volume

Apply the PVC first, then the stateful Deployment:

```bash
kubectl apply -f k8s/2-pvc.yaml
kubectl apply -f k8s/3-postgres-stateful.yaml
```

Wait for the Pod to be Ready:

```bash
kubectl get pods -l app=postgres-stateful
kubectl get pvc postgres-data
```

The PVC should show `Bound`.

### 2.3 Create data again

```bash
kubectl exec -it $(kubectl get pod -l app=postgres-stateful -o jsonpath='{.items[0].metadata.name}') -- psql -U labuser -d labdb -c "
CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT);
INSERT INTO users (name) VALUES ('Bob');
SELECT * FROM users;
"
```

You should see **Bob**.

### 2.4 Delete the Pod again

**WARNING: DELETING POD NOW.** This time, data lives on the PersistentVolume. The new Pod will mount the same PVC.

```bash
kubectl delete pod -l app=postgres-stateful
```

Wait for the new Pod to be Running:

```bash
kubectl get pods -l app=postgres-stateful -w
# Ctrl+C when Running
```

### 2.5 Check for Bob

```bash
kubectl exec -it $(kubectl get pod -l app=postgres-stateful -o jsonpath='{.items[0].metadata.name}') -- psql -U labuser -d labdb -c "SELECT * FROM users;"
```

**Result:** **Bob is still there.** The table and data survived because they were stored on the PVC at `/var/lib/postgresql/data`. New Pod, same volume, same data.

---

## Summary

| Setup              | Volume | Delete Pod | Data after new Pod |
|--------------------|--------|------------|----------------------|
| **Stateless**      | No     | Yes        | **Lost** (Alice gone) |
| **Stateful (PVC)** | Yes    | Yes        | **Survives** (Bob still there) |

- **No PVC:** Data lives only in the container filesystem → lost when the Pod is removed.
- **With PVC:** Data lives on the cluster’s storage → survives Pod deletion and is reused when a new Pod mounts the same claim.

---

## Cleanup

```bash
kubectl delete -f k8s/3-postgres-stateful.yaml
kubectl delete -f k8s/2-pvc.yaml
# If you left stateless running:
kubectl delete -f k8s/1-postgres-stateless.yaml
```
