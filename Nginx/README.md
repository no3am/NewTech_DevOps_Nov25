# Nginx Load Balancing Lab

## Objective

Learn how Nginx acts as a load balancer, distributing incoming requests across multiple backend containers using Round Robin algorithm.

## What You'll See

When you refresh the page multiple times, you'll see different Container IDs. This demonstrates that Nginx is distributing requests across 3 different Flask containers.

## Prerequisites

- Docker installed
- Docker Compose installed

## Lab Steps

### Step 1: Start the Application

**Command:**
```bash
docker-compose up --build
```

**What happens:**
- Builds the Flask application image
- Starts 3 replicas of the Flask app (each with a unique hostname)
- Starts Nginx as a reverse proxy/load balancer
- Nginx listens on port 80 and forwards requests to the Flask containers

**Expected Output:**
```
Creating nginx_app_1 ... done
Creating nginx_app_2 ... done
Creating nginx_app_3 ... done
Creating nginx_nginx_1 ... done
Attaching to nginx_app_1, nginx_app_2, nginx_app_3, nginx_nginx_1
```

### Step 2: Test the Load Balancer

1. **Open your web browser**
2. **Navigate to:** `http://localhost`
3. **Refresh the page 10 times**

**What you should see:**

- **First refresh:** `Hello! I am Container ID: nginx_app_1`
- **Second refresh:** `Hello! I am Container ID: nginx_app_2`
- **Third refresh:** `Hello! I am Container ID: nginx_app_3`
- **Fourth refresh:** `Hello! I am Container ID: nginx_app_1` (starts over)
- And so on...

**Or use curl:**
```bash
for i in {1..10}; do
  echo "Request $i:"
  curl http://localhost
  echo -e "\n"
  sleep 1
done
```

## Understanding the Results

### Question: Why does the Container ID change?

**Answer: Nginx Round Robin Load Balancing**

Nginx uses a **Round Robin** algorithm by default. This means:

1. **Request 1** → Goes to Container 1
2. **Request 2** → Goes to Container 2
3. **Request 3** → Goes to Container 3
4. **Request 4** → Goes back to Container 1 (round robin cycle repeats)

This distributes the load evenly across all available containers, ensuring:
- **High Availability**: If one container fails, others can still serve requests
- **Performance**: Work is distributed, preventing any single container from being overwhelmed
- **Scalability**: Easy to add more containers to handle increased traffic

## Architecture

```
Internet Request
      ↓
   Nginx (Port 80)
      ↓
   Load Balancer
      ↓
   ┌──────┬──────┬──────┐
   │ App1 │ App2 │ App3 │
   │:5000 │:5000 │:5000 │
   └──────┴──────┴──────┘
```

- **Nginx** acts as the entry point (reverse proxy)
- **3 Flask containers** run the actual application
- Nginx distributes requests using Round Robin

## How It Works

### nginx.conf Explained

```nginx
upstream my_app {
    server app:5000;  # Points to the 'app' service on port 5000
}

server {
    listen 80;
    location / {
        proxy_pass http://my_app;  # Forward requests to upstream
    }
}
```

- **`upstream my_app`**: Defines a group of backend servers
- **`server app:5000`**: Docker Compose resolves `app` to all 3 replicas
- **`proxy_pass http://my_app`**: Forwards requests to the upstream group

### docker-compose.yml Explained

```yaml
services:
  app:
    deploy:
      replicas: 3  # Creates 3 identical containers
      
  nginx:
    depends_on:
      - app  # Waits for app containers to be ready
```

- **`replicas: 3`**: Creates 3 instances of the Flask app
- **`depends_on`**: Ensures app containers start before Nginx

## Cleanup

When you're done:

**Stop and remove containers:**
```bash
docker-compose down
```

**Remove everything including volumes:**
```bash
docker-compose down -v
```

## Key Takeaways

1. **Load Balancing**: Distributes traffic across multiple servers/containers
2. **Round Robin**: Simple algorithm that cycles through servers in order
3. **High Availability**: If one container fails, others continue serving
4. **Scalability**: Easy to add more replicas to handle more traffic
5. **Reverse Proxy**: Nginx sits in front of your application, handling routing

## Next Steps

- Experiment with different load balancing algorithms (ip_hash, least_conn)
- Add health checks to remove unhealthy containers
- Scale up to 5 or 10 replicas and observe the distribution
- Learn about sticky sessions (session affinity)
