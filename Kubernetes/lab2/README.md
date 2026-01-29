# Kubernetes Lab 2: The Magic of Deployments

## Objective

Learn about Deployments - Kubernetes' way of managing Pods with self-healing and scaling capabilities. Discover the power of declarative configuration using YAML files.

## Prerequisites

- Completed Lab 1 (My First Pod)
- Minikube running
- Basic understanding of Pods

## What is a Deployment?

A **Deployment** is a Kubernetes object that manages Pods for you. Instead of manually creating individual Pods, you tell Kubernetes:
- "I want 3 copies of this application running"
- Kubernetes ensures 3 Pods are always running
- If one dies, Kubernetes automatically creates a replacement

This is called **self-healing** - one of Kubernetes' superpowers!

## Lab Tasks

### Task 1: Examine the Deployment YAML

Before we apply anything, let's understand what we're working with.

**Open the file:**
```bash
cat nginx-deployment.yaml
```

**Key Concepts:**

1. **`replicas: 3`** - You're telling Kubernetes: "I want 3 Pods running at all times"
2. **`selector`** - Kubernetes uses this to find Pods that belong to this Deployment
3. **`template`** - The blueprint for creating new Pods (the Pod specification)

The `selector.matchLabels` must match the `template.metadata.labels`. This is how Kubernetes knows which Pods belong to this Deployment.

---

### Task 2: Apply the Deployment

Now let's create the Deployment using the declarative approach with YAML.

**Command:**
```bash
kubectl apply -f nginx-deployment.yaml
```

**Expected Output:**
```
deployment.apps/nginx-deployment created
```

**What just happened?**
- Kubernetes read your YAML file
- It created a Deployment object
- The Deployment controller started creating Pods to match your desired state (3 replicas)

---

### Task 3: Observe the Deployment

Let's see what Kubernetes created for us.

#### 3.1 Check the Deployment

**Command:**
```bash
kubectl get deployments
```

**Expected Output:**
```
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   3/3     3            3           10s
```

**Understanding the output:**
- `READY` - 3/3 means 3 Pods are ready out of 3 desired
- `UP-TO-DATE` - 3 Pods are running the latest configuration
- `AVAILABLE` - 3 Pods are available to serve traffic
- `AGE` - How long the Deployment has existed

#### 3.2 Check the Pods

**Command:**
```bash
kubectl get pods
```

**Expected Output:**
```
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-7d4f8b9c4f-abc12   1/1     Running   0          15s
nginx-deployment-7d4f8b9c4f-def34   1/1     Running   0          15s
nginx-deployment-7d4f8b9c4f-ghi56   1/1     Running   0          15s
```

**Notice:**
- All Pods have similar names: `nginx-deployment-<hash>-<random>`
- The hash (`7d4f8b9c4f`) is the ReplicaSet identifier
- The random suffix (`abc12`, `def34`, `ghi56`) identifies each Pod
- All 3 Pods are `Running` and `READY`

**Get more details:**
```bash
kubectl get pods -o wide
```

This shows which node each Pod is running on and their IP addresses.

---

### Task 4: The Chaos Test - Self-Healing in Action! 🎯

This is where the magic happens. Let's see Kubernetes' self-healing in action.

#### Step 1: Pick a Pod to Delete

**Command:**
```bash
kubectl get pods
```

**Copy one of the Pod names.** For example: `nginx-deployment-7d4f8b9c4f-abc12`

#### Step 2: Delete the Pod

**Command:**
```bash
kubectl delete pod <pod-name>
```

Replace `<pod-name>` with the Pod name you copied.

**Example:**
```bash
kubectl delete pod nginx-deployment-7d4f8b9c4f-abc12
```

**Expected Output:**
```
pod "nginx-deployment-7d4f8b9c4f-abc12" deleted
```

#### Step 3: Immediately Check Pods Again

**Command:**
```bash
kubectl get pods
```

**Expected Output:**
```
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-7d4f8b9c4f-def34   1/1     Running   0          2m
nginx-deployment-7d4f8b9c4f-ghi56   1/1     Running   0          2m
nginx-deployment-7d4f8b9c4f-xyz78   1/1     Running   0          4s    ← NEW POD!
```

**What happened?**
- You deleted one Pod
- Kubernetes immediately detected that only 2 Pods were running
- Your Deployment says `replicas: 3`, so Kubernetes created a new Pod
- The new Pod (`xyz78`) has `AGE: 4s` - it was just created!

**Watch it happen in real-time:**
```bash
kubectl get pods -w
```

Then delete a Pod in another terminal. You'll see the new Pod appear instantly!

#### Step 4: Understand the Magic

**Key Takeaway:**
> **You told Kubernetes you wanted 3 Pods. You deleted one. Kubernetes saw 2, so it created 1 more to keep your promise.**

This is **self-healing** - Kubernetes maintains your desired state automatically. You don't need to manually recreate Pods when they fail.

**Check the Deployment status:**
```bash
kubectl get deployments
```

You should still see `READY: 3/3` - Kubernetes restored the desired state!

---

### Task 5: Scale Up - Watch the Army Grow

Now let's scale from 3 Pods to 10 Pods and watch Kubernetes create the additional Pods.

#### Step 1: Edit the YAML File

**Open the file:**
```bash
nano nginx-deployment.yaml
```

Or use your preferred editor (vim, code, etc.)

**Change this line:**
```yaml
replicas: 3
```

**To:**
```yaml
replicas: 10
```

**Save the file.**

#### Step 2: Apply the Updated Configuration

**Command:**
```bash
kubectl apply -f nginx-deployment.yaml
```

**Expected Output:**
```
deployment.apps/nginx-deployment configured
```

Notice it says "configured" not "created" - Kubernetes updated the existing Deployment.

#### Step 3: Watch the Pods Multiply

**Command:**
```bash
kubectl get pods -w
```

**Expected Output (watch it update in real-time):**
```
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-7d4f8b9c4f-def34   1/1     Running   0          5m
nginx-deployment-7d4f8b9c4f-ghi56   1/1     Running   0          5m
nginx-deployment-7d4f8b9c4f-xyz78   1/1     Running   0          3m
nginx-deployment-7d4f8b9c4f-abc90   0/1     Pending   0          0s    ← NEW
nginx-deployment-7d4f8b9c4f-def01   0/1     Pending   0          0s    ← NEW
nginx-deployment-7d4f8b9c4f-ghi23   0/1     Pending   0          0s    ← NEW
nginx-deployment-7d4f8b9c4f-jkl45   0/1     Pending   0          0s    ← NEW
nginx-deployment-7d4f8b9c4f-mno67   0/1     Pending   0          0s    ← NEW
nginx-deployment-7d4f8b9c4f-pqr89   0/1     Pending   0          0s    ← NEW
nginx-deployment-7d4f8b9c4f-stu01   0/1     Pending   0          0s    ← NEW
```

Watch as the new Pods transition from `Pending` → `ContainerCreating` → `Running`!

Press `Ctrl+C` to stop watching.

**Check the final count:**
```bash
kubectl get pods
```

**Expected Output:**
```
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-7d4f8b9c4f-def34   1/1     Running   0          6m
nginx-deployment-7d4f8b9c4f-ghi56   1/1     Running   0          6m
nginx-deployment-7d4f8b9c4f-xyz78   1/1     Running   0          4m
nginx-deployment-7d4f8b9c4f-abc90   1/1     Running   0          30s
nginx-deployment-7d4f8b9c4f-def01   1/1     Running   0          30s
nginx-deployment-7d4f8b9c4f-ghi23   1/1     Running   0          30s
nginx-deployment-7d4f8b9c4f-jkl45   1/1     Running   0          30s
nginx-deployment-7d4f8b9c4f-mno67   1/1     Running   0          30s
nginx-deployment-7d4f8b9c4f-pqr89   1/1     Running   0          30s
nginx-deployment-7d4f8b9c4f-stu01   1/1     Running   0          30s
```

**10 Pods running!** 🎉

**Verify the Deployment:**
```bash
kubectl get deployments
```

**Expected Output:**
```
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   10/10   10           10          10m
```

Perfect! `READY: 10/10` - all 10 Pods are running.

---

### Task 6: Alternative Scaling Method (Imperative)

You can also scale without editing the YAML file using an imperative command:

**Command:**
```bash
kubectl scale deployment nginx-deployment --replicas=5
```

**Expected Output:**
```
deployment.apps/nginx-deployment scaled
```

**Check the Pods:**
```bash
kubectl get pods
```

You should now see 5 Pods (Kubernetes will delete 5 to match the new desired state).

**Note:** While this works, the declarative approach (editing YAML and applying) is preferred because:
- Your YAML file stays in sync with reality
- You can version control your changes
- It's the "GitOps" way of doing things

---

## Summary

In this lab, you learned:

✅ How to create a Deployment using YAML (declarative approach)  
✅ How Deployments manage multiple Pod replicas  
✅ How Kubernetes self-heals by automatically replacing dead Pods  
✅ How to scale Deployments up and down  
✅ The relationship between Deployments, ReplicaSets, and Pods  

## Key Takeaways

1. **Deployments > Pods**: Use Deployments instead of creating Pods directly. They provide self-healing, scaling, and rolling updates.

2. **Desired State**: You declare what you want (3 Pods), and Kubernetes makes it happen. If reality doesn't match, Kubernetes fixes it.

3. **Self-Healing**: When a Pod dies, Kubernetes automatically creates a replacement. You don't need to babysit your applications.

4. **Scaling is Easy**: Change `replicas` in YAML and apply, or use `kubectl scale`. Kubernetes handles the rest.

5. **Declarative > Imperative**: Using YAML files (declarative) is better than running commands (imperative) because your configuration is version-controlled and reproducible.

## Architecture: Deployment → ReplicaSet → Pods

```
Deployment (nginx-deployment)
    └── ReplicaSet (nginx-deployment-7d4f8b9c4f)
        ├── Pod (nginx-deployment-7d4f8b9c4f-abc12)
        ├── Pod (nginx-deployment-7d4f8b9c4f-def34)
        └── Pod (nginx-deployment-7d4f8b9c4f-ghi56)
```

- **Deployment**: Manages the desired state and handles rolling updates
- **ReplicaSet**: Ensures the correct number of Pods are running
- **Pods**: The actual containers running your application

You can see the ReplicaSet:
```bash
kubectl get replicasets
```

---

## Cleanup

When you're done experimenting:

**Delete the Deployment:**
```bash
kubectl delete deployment nginx-deployment
```

This will automatically delete the ReplicaSet and all Pods.

**Verify everything is gone:**
```bash
kubectl get pods
kubectl get deployments
```

---

## Next Steps

- Lab 3: Learn about Services (exposing Pods to the network)
- Lab 4: Learn about ConfigMaps and Secrets
- Lab 5: Rolling updates and rollbacks

## Troubleshooting

**Pods stuck in Pending:**
- Check if Minikube has enough resources: `minikube status`
- Check events: `kubectl describe pod <pod-name>`

**Deployment not scaling:**
- Verify the YAML syntax: `kubectl apply -f nginx-deployment.yaml --dry-run=client`
- Check Deployment status: `kubectl describe deployment nginx-deployment`

**Can't see new Pods after scaling:**
- Wait a few seconds for Pods to be created
- Check if there are resource constraints: `kubectl describe nodes`
