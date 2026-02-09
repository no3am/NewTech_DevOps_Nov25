# Kubernetes Lab 1: My First Pod

## Objective

Learn how to create, inspect, and interact with your first Kubernetes Pod using imperative commands.

## Prerequisites

- Minikube installed
- kubectl installed
- Basic understanding of containers

## Lab Tasks

### Task 1: Start Minikube

First, we need to start a local Kubernetes cluster using Minikube.

**Command:**
```bash
minikube start
```

**Expected Output:**
```
😄  minikube v1.32.0 on Darwin 14.0
✨  Automatically selected the docker driver
📦  Preparing Kubernetes v1.28.3 on Docker 24.0.7 ...
🔗  Configuring bridge CNI (Container Networking Interface) ...
🔧  Verifying Kubernetes components...
✅  Kubernetes control plane and worker nodes are running!
```

**Verify the cluster is running:**
```bash
kubectl cluster-info
```

**Expected Output:**
```
Kubernetes control plane is running at https://127.0.0.1:6443
CoreDNS is running at https://127.0.0.1:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

---

### Task 2: Create Your First Pod (Imperative Command)

We'll use the **imperative** approach with `kubectl run` to create a Pod. This is the quickest way to get started, though later you'll learn the declarative YAML approach.

**Command:**
```bash
kubectl run nginx-pod --image=nginx:latest
```

**What this does:**
- `kubectl run` - Creates a Pod using an imperative command
- `nginx-pod` - The name of your Pod
- `--image=nginx:latest` - The container image to use

**Expected Output:**
```
pod/nginx-pod created
```

**Note:** In newer versions of kubectl, `kubectl run` creates a Deployment by default. If you see a deployment created instead, you can still access the pod. Alternatively, you can use:
```bash
kubectl run nginx-pod --image=nginx:latest --restart=Never
```

The `--restart=Never` flag ensures it creates a Pod directly, not a Deployment.

#### Alternative: Create Pod from YAML (Declarative)

You can create the same Pod using the declarative approach with the included `pod.yaml`:

**Command:**
```bash
kubectl apply -f pod.yaml
```

**Expected Output:**
```
pod/nginx-pod created
```

The `pod.yaml` file defines the same nginx Pod: name `nginx-pod`, image `nginx:latest`, container port 80.

---

### Task 3: Inspect Your Pod

#### 3.1 List All Pods

**Command:**
```bash
kubectl get pods
```

**Expected Output:**
```
NAME        READY   STATUS    RESTARTS   AGE
nginx-pod   1/1     Running   0          10s
```

**Understanding the output:**
- `NAME` - The name of your Pod
- `READY` - Number of containers ready vs total (1/1 means 1 container is ready out of 1 total)
- `STATUS` - Current state (Running, Pending, Error, etc.)
- `RESTARTS` - Number of times the container has restarted
- `AGE` - How long the Pod has been running

**Watch the Pod status in real-time:**
```bash
kubectl get pods -w
```

Press `Ctrl+C` to stop watching.

#### 3.2 Describe the Pod

The `describe` command shows detailed information about your Pod, including important events.

**Command:**
```bash
kubectl describe pod nginx-pod
```

**Expected Output:**
```
Name:             nginx-pod
Namespace:        default
Priority:         0
Node:             minikube/192.168.49.2
Start Time:       Mon, 01 Jan 2024 10:00:00 -0500
Labels:           run=nginx-pod
Annotations:      <none>
Status:           Running
IP:               10.244.0.5
IPs:
  IP:  10.244.0.5
Containers:
  nginx-pod:
    Container ID:   docker://abc123def456...
    Image:          nginx:latest
    Image ID:       docker-pullable://nginx@sha256:...
    Port:           <none>
    Host Port:      <none>
    State:          Running
      Started:      Mon, 01 Jan 2024 10:00:15 -0500
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:         <none>
Conditions:
  Type              Status
  Initialized       True
  Ready             True
  ContainersReady   True
  PodScheduled      True
Volumes:            <none>
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  30s   default-scheduler  Successfully assigned default/nginx-pod to minikube
  Normal  Pulling    25s   kubelet            Pulling image "nginx:latest"
  Normal  Pulled     20s   kubelet            Successfully pulled image "nginx:latest"
  Normal  Created    15s   kubelet            Created container nginx-pod
  Normal  Started    15s   kubelet            Started container nginx-pod
```

**Key Lesson: The Events Section**

Look at the `Events:` section at the bottom. This shows the lifecycle of your Pod:

1. **Scheduled** - Kubernetes scheduler assigned the Pod to a node
2. **Pulling** - Kubernetes is downloading the nginx image
3. **Pulled** - Image successfully downloaded
4. **Created** - Container was created
5. **Started** - Container started running

This is incredibly useful for debugging! If something goes wrong, the Events section will tell you exactly what happened.

**Get just the events:**
```bash
kubectl describe pod nginx-pod | grep -A 10 Events
```

---

### Task 4: Access the Pod (Port Forwarding)

Pods have internal IP addresses that are only accessible within the Kubernetes cluster. To access the Nginx web server from your local machine, we need to use **port forwarding**.

**Command:**
```bash
kubectl port-forward pod/nginx-pod 8080:80
```

**What this does:**
- `kubectl port-forward` - Creates a tunnel from your local machine to the Pod
- `pod/nginx-pod` - The Pod to forward to
- `8080:80` - Map local port 8080 to container port 80 (Nginx's default port)

**Expected Output:**
```
Forwarding from 127.0.0.1:8080 -> 80
Forwarding from [::1]:8080 -> 80
```

**Keep this terminal open!** The port-forward command runs in the foreground. Open a new terminal for other commands.

**Test the connection:**

1. Open your web browser
2. Navigate to: `http://localhost:8080`
3. You should see the Nginx welcome page!

**Or use curl:**
```bash
curl http://localhost:8080
```

You should see the HTML content of the Nginx welcome page.

**Stop port forwarding:** Press `Ctrl+C` in the terminal where port-forward is running.

---

### Task 5: Cleanup

When you're done experimenting, delete the Pod.

**Command:**
```bash
kubectl delete pod nginx-pod
```

**Expected Output:**
```
pod "nginx-pod" deleted
```

**Verify it's gone:**
```bash
kubectl get pods
```

**Expected Output:**
```
No resources found in default namespace.
```

**Optional: Stop Minikube (if you're done for the day)**
```bash
minikube stop
```

---

## Summary

In this lab, you learned:

✅ How to start a local Kubernetes cluster with Minikube  
✅ How to create a Pod using imperative commands (`kubectl run`)  
✅ How to list and inspect Pods (`kubectl get pods`, `kubectl describe pod`)  
✅ How to understand Pod events and lifecycle  
✅ How to access Pods from your local machine using port forwarding  
✅ How to delete Pods when done  

## Key Takeaways

1. **Imperative vs Declarative**: You used `kubectl run` (imperative). Later you'll learn YAML files (declarative).

2. **Pod IPs are Internal**: Pod IPs like `10.244.0.5` are only accessible within the cluster. Use port-forwarding or Services to access them externally.

3. **Events are Your Friend**: The `kubectl describe` command shows events that help you understand what Kubernetes is doing and debug issues.

4. **Pods are Ephemeral**: When you delete a Pod, it's gone. In production, you'll use Deployments to ensure Pods are recreated if they fail.

## Next Steps

- Lab 2: Learn about Deployments and ReplicaSets
- Lab 3: Learn about Services and exposing Pods
- Lab 4: Create Pods using YAML files (declarative approach)

## Troubleshooting

**Pod stuck in "Pending" status:**
- Check if Minikube is running: `minikube status`
- Check events: `kubectl describe pod nginx-pod`

**Port forwarding doesn't work:**
- Make sure the Pod is running: `kubectl get pods`
- Check if port 8080 is already in use on your machine
- Try a different port: `kubectl port-forward pod/nginx-pod 9000:80`

**Can't pull image:**
- Check your internet connection
- Verify image name is correct: `kubectl describe pod nginx-pod`
