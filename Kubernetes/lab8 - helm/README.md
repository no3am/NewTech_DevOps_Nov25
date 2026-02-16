# Kubernetes Lab 8: Helm Fundamentals

## Context

So far you have been managing apps by copy-pasting multiple YAML files (Deployment, Service, ConfigMap)—**"YAML Hell."** Helm is the solution: think of it as the **package manager** (or **apt-get**) for Kubernetes. You define your app once as a **Chart**, then **Install**, **Upgrade**, and **Rollback** with simple commands.

## Goal

Create a custom Helm Chart from scratch (not from `helm create`) to see how the **"Mad Libs" templating engine** works. You will run the full lifecycle: **Install → Upgrade → Break → Rollback.**

**Key idea:** **values.yaml** holds configuration (image, replicas, environment). The templates in `templates/` use **Go templates** to inject those values. This **separates configuration from logic**—you change settings in one place without editing YAML manifests.

---

## Prerequisites

- A Kubernetes cluster and `kubectl` configured.
- **Helm 3** installed. Check with: `helm version`.

---

## The Chart

The lab uses the `my-chart/` directory:

- **Chart.yaml** — Chart metadata (name: `web-server`, version: `0.1.0`).
- **values.yaml** — Default settings: `image`, `replicaCount`, `environment`. **This is where you change config.**
- **templates/deployment.yaml** — A standard Deployment with `{{ .Values.image }}`, `{{ .Values.replicaCount }}`, and `env: {{ .Values.environment }}`.

---

## Step 1: The Install

Install the chart. This creates a **Release** (an instance) from the **Chart** (the package).

```bash
helm install my-release ./my-chart
```

- **Chart** = the package (the `my-chart/` folder).
- **Release** = the deployed instance (named `my-release`).

Verify:

```bash
kubectl get pods
kubectl get deployment
```

You should see one Pod (from `replicaCount: 1` in **values.yaml**).

---

## Step 2: The Upgrade

Change **values.yaml**: set **replicaCount** to **3**.

Then run:

```bash
helm upgrade my-release ./my-chart
```

Helm applies the new values. This creates **Revision 2**. Confirm:

```bash
helm history my-release
```

You should see Revision 1 (install) and Revision 2 (upgrade). Then:

```bash
kubectl get pods
```

You should see **3** Pods.

---

## Step 3: The Break

In **values.yaml**, set the image to a **bad tag** so the image cannot be pulled:

```yaml
image: nginx:broken-tag
```

Upgrade again:

```bash
helm upgrade my-release ./my-chart
```

This becomes **Revision 3**. Watch the Pods:

```bash
kubectl get pods -w
```

Pods will stay in `ImagePullBackOff` or `ErrImagePull` because `nginx:broken-tag` does not exist. You have deliberately **broken** the release.

---

## Step 4: The Rollback

Helm keeps a history of revisions. **Rollback** to the last good state (Revision 2):

```bash
helm rollback my-release 2
```

This is the **"Undo Button"**—Helm reapplies the manifests from Revision 2 (3 replicas, correct image). Watch the Pods recover:

```bash
kubectl get pods
```

You should see 3 healthy Pods again with the original image.

---

## Summary

| Step   | Command                          | What it does                          |
|--------|----------------------------------|----------------------------------------|
| Install | **helm install my-release ./my-chart** | Creates the release (Revision 1)       |
| Upgrade | **helm upgrade my-release ./my-chart** | Applies new values (Revision 2, 3…)   |
| Rollback | **helm rollback my-release 2**       | Restores a previous revision (undo)    |

**values.yaml** lets you separate **configuration** (what image? how many replicas? which env?) from **logic** (the Deployment template). Change config in one file; Helm does the rest.
