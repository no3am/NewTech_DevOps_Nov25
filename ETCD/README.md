# ETCD Watch Mechanism Lab

## Objective

Learn how etcd's Watch mechanism works and understand how Kubernetes Controllers use this same pattern to react to cluster changes in real-time.

## What You'll Learn

- How etcd Watch works (event-driven, not polling)
- How Kubernetes Controllers monitor cluster state
- The difference between polling and event-driven architectures
- How to set up a watcher that reacts instantly to changes

## Architecture

```
┌─────────────┐
│   Writer    │  (Manual script - simulates kubectl apply)
│  (writer.py)│
└──────┬──────┘
       │ Writes to
       ↓
┌─────────────┐
│    etcd     │  (Key-value store - Kubernetes uses this!)
│  (Port 2379)│
└──────┬──────┘
       │ Notifies
       ↓
┌─────────────┐
│   Watcher   │  (Watches for changes - like a K8s Controller)
│ (watcher.py)│
└─────────────┘
```

## Prerequisites

- Docker installed
- Docker Compose installed
- Python 3.11+ (for running writer.py locally, or use the container)

## Lab Steps

### Step 1: Start the Services

Start etcd and the watcher service:

```bash
docker-compose up --build
```

**What happens:**
- Starts etcd server (the distributed key-value store)
- Starts the watcher service (monitors `/config/background_color` key)
- Watcher prints: "Waiting for updates..."

**Expected Output:**
```
etcd_server  | etcd is ready to serve client requests
etcd_watcher | Connecting to etcd at etcd:2379...
etcd_watcher | ✓ Connected to etcd successfully!
etcd_watcher | Watching key: /config/background_color
etcd_watcher | Waiting for updates...
```

### Step 2: Change the Key Value

In a **new terminal**, run the writer script to change the key:

```bash
python writer.py red
```

**What happens:**
- The writer connects to etcd
- Writes "red" to the key `/config/background_color`
- **Instantly**, the watcher detects the change!

**Expected Output in Watcher:**
```
============================================================
🚨 DETECTED CHANGE! New Color is: red
============================================================
Event Type: PutEvent
Key: /config/background_color
Value: red
Timestamp: 2024-01-15 10:30:45

💡 This is exactly how Kubernetes Controllers react to changes!
   - No polling needed
   - Instant notification
   - Event-driven architecture
------------------------------------------------------------

🔍 Continuing to watch...
```

### Step 3: Change It Again

Try different values:

```bash
python writer.py blue
python writer.py green
python writer.py "#FF5733"
```

Each time you run the writer, the watcher **immediately** detects the change - no polling, no delay!

### Step 4: Observe the Instant Reaction

Notice that:
- ✅ The watcher reacts **instantly** (no delay)
- ✅ No polling is happening (check the logs - no repeated checks)
- ✅ Event-driven architecture (only reacts when something changes)

## How This Relates to Kubernetes

### Kubernetes Controllers Use the Same Pattern

1. **You run a command:**
   ```bash
   kubectl apply -f deployment.yaml
   ```

2. **Kubernetes API Server writes to etcd:**
   - The Deployment object is stored in etcd
   - Similar to: `writer.py` writing to etcd

3. **Controller watches etcd:**
   - Deployment Controller is watching for Deployment objects
   - Similar to: `watcher.py` watching `/config/background_color`

4. **Controller reacts instantly:**
   - Controller detects the new Deployment
   - Controller creates ReplicaSets and Pods
   - Similar to: Watcher printing "DETECTED CHANGE!"

### Key Concepts

| This Lab | Kubernetes Equivalent |
|----------|----------------------|
| `writer.py` writes to etcd | `kubectl apply` → API Server → etcd |
| `watcher.py` watches key | Controller watches resource type |
| Change detected instantly | Controller reacts to resource changes |
| Event-driven (no polling) | Controllers use Watch API (no polling) |

## Running the Writer Script

### Option 1: Run Locally (Recommended)

Make sure you have Python 3.11+ and install dependencies:

```bash
pip install -r requirements.txt
python writer.py red
```

### Option 2: Run in Container

If you don't have Python locally, run the writer in a container:

```bash
docker run --rm -it \
  --network etcd_default \
  -v $(pwd):/app \
  -w /app \
  -e ETCD_HOST=etcd \
  -e ETCD_PORT=2379 \
  python:3.11-slim \
  sh -c "pip install -q etcd3==0.1.5 && python writer.py red"
```

Or use docker-compose exec:

```bash
docker-compose exec watcher python -c "
import etcd3
client = etcd3.client(host='etcd', port=2379)
client.put('/config/background_color', 'red')
print('Updated to red')
"
```

## Understanding the Code

### watcher.py - The Watch Mechanism

```python
# This is the key line - sets up a watch
events_iterator, cancel = client.watch_prefix(WATCH_KEY)

# This loop waits for events (not polling!)
for event in events_iterator:
    # React to the change immediately
    print("DETECTED CHANGE!")
```

**Key Points:**
- `watch_prefix()` subscribes to changes (event-driven)
- The loop blocks until an event occurs
- No CPU wasted on polling
- Instant reaction when key changes

### writer.py - Simulating API Server

```python
# This writes to etcd (like kubectl apply does)
client.put(WATCH_KEY, new_value)
```

**Key Points:**
- Simple write operation
- Watcher is notified automatically
- No need to manually notify watchers

## Common Issues & Solutions

### Issue: "Failed to connect to etcd"

**Solution:** Make sure etcd is running:
```bash
docker-compose up
```

### Issue: "Connection refused" when running writer.py

**Solution:** Check ETCD_HOST and ETCD_PORT:
- If running locally: `ETCD_HOST=localhost ETCD_PORT=2379 python writer.py red`
- If etcd is in Docker: Make sure ports are exposed (they are in docker-compose.yml)

### Issue: Watcher doesn't detect changes

**Solution:** 
1. Check that watcher is connected: Look for "✓ Connected to etcd successfully!"
2. Verify the key path matches: `/config/background_color`
3. Check etcd logs: `docker-compose logs etcd`

## Cleanup

When you're done:

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (clears etcd data)
docker-compose down -v
```

## Key Takeaways

1. **Watch is Event-Driven**: No polling needed - etcd notifies watchers when keys change
2. **Instant Reaction**: Changes are detected immediately (milliseconds, not seconds)
3. **Efficient**: No CPU wasted checking repeatedly
4. **Kubernetes Pattern**: This is exactly how Controllers work in Kubernetes
5. **Scalable**: Can watch thousands of keys efficiently

## Next Steps

- Experiment with watching multiple keys
- Try watching a key prefix (e.g., `/config/*`)
- Learn about etcd transactions
- Explore Kubernetes Controller patterns
- Study how etcd handles network partitions

## Bonus Challenges

1. **Watch Multiple Keys**: Modify watcher.py to watch both `/config/background_color` and `/config/font_size`

2. **Add a Web UI**: Create a simple Flask app that displays the current color and allows changing it

3. **Simulate Multiple Controllers**: Create multiple watcher services watching different keys

4. **Add Health Checks**: Implement a health check endpoint that verifies etcd connectivity

---

**Remember**: This Watch mechanism is the foundation of how Kubernetes Controllers work. When you understand this, you understand a core part of Kubernetes architecture! 🚀
