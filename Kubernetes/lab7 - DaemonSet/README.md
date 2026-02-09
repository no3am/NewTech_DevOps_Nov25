# Kubernetes Lab 7: DaemonSets

## Objective

Use a **DaemonSet** so that one instance of a Pod runs on **every node** in the cluster. This is the usual pattern for node-level “background” services such as:

- **Log collectors** (e.g. Fluentd)
- **Monitoring agents** (e.g. Node Exporter)
- **Networking / storage plugins**

In this lab you will:

- Deploy a **Fluentd** logging agent via a DaemonSet.
- See that **Desired** Pod count matches the number of nodes (one Pod per node).
- See that **no node runs more than one** Fluentd Pod.
- (On a multi-node cluster) See that when a **new node is added**, a new Pod is scheduled on it automatically.
- See how DaemonSets **ignore normal replica counts** and scheduling constraints to get node-level coverage.

---

## Prerequisites

- A Kubernetes cluster (v1.20+).
- **Ideal:** At least **two worker nodes** so you can clearly see “one Pod per node.”  
  On Minikube you typically have one node; the DaemonSet will still run one Pod on that node.

---

## The Exercise

### 1. DaemonSet (`fluentd-ds.yaml`)

The manifest defines:

- A **DaemonSet** named `fluentd-logging` in `kube-system`.
- **Tolerations** so the Pod can run on control-plane nodes that have `NoSchedule` taints (`node-role.kubernetes.io/control-plane` and `node-role.kubernetes.io/master`).
- A single container: **Fluentd** (log forwarder), with resource limits/requests.
- A **hostPath** volume mounting the node’s `/var/log` so Fluentd can read node logs.

There is **no `replicas`** field: the DaemonSet controller ensures one Pod per node.

---

## Deployment

Apply the manifest:

```bash
kubectl apply -f k8s/fluentd-ds.yaml
```

---

## Verification

### 1. DaemonSet status

Check that **Desired** matches the number of nodes (and that **Current** matches **Desired**):

```bash
kubectl get ds -n kube-system fluentd-logging
```

Example (3-node cluster):

```
NAME              DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
fluentd-logging   3         3         3       3            3          <none>          1m
```

**Desired = number of (schedulable) nodes.** That’s the “one Pod per node” behavior.

### 2. Pod distribution (one per node)

List the Pods with node names. You should see **at most one** Fluentd Pod per node:

```bash
kubectl get pods -n kube-system -o wide -l name=fluentd-logging
```

Example:

```
NAME                    READY   STATUS    NODE
fluentd-logging-xxxxx   1/1     Running   node-1
fluentd-logging-yyyyy   1/1     Running   node-2
fluentd-logging-zzzzz   1/1     Running   node-3
```

No node should have two Fluentd Pods.

### 3. (Optional) Add a node and watch a new Pod appear

If your cluster has multiple nodes and you can add one (e.g. scale a node pool, or add a worker):

1. Note the current number of Fluentd Pods: `kubectl get pods -n kube-system -l name=fluentd-logging`.
2. Add the new node and wait until it is Ready.
3. Run again: `kubectl get pods -n kube-system -l name=fluentd-logging` and `kubectl get ds -n kube-system fluentd-logging`.

You should see **Desired** and the Pod count increase by one, and a new Fluentd Pod on the new node. The DaemonSet ensures node-level coverage without manual scaling.

---

## Summary

| Aspect | DaemonSet behavior |
|--------|--------------------|
| **Scheduling** | One Pod per node; no `replicas` field. |
| **New nodes** | When a new node joins, a new Pod is scheduled on it automatically. |
| **Limits** | Ignores normal replica/scheduling limits to achieve node coverage. |
| **Use cases** | Log collectors, monitoring agents, networking/storage plugins. |

---

## Cleanup

```bash
kubectl delete -f k8s/fluentd-ds.yaml
```
