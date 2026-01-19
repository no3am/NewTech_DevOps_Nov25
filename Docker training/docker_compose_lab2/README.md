# Docker Compose Lab 2: The Easy Way

This lab demonstrates how Docker Compose simplifies multi-container applications compared to manual shell scripts.

## Old Way vs New Way

### The Old Way (Manual Script)
- Create network manually: `docker network create class-net`
- Start database container with all flags: `docker run -d --name postgres-db --network class-net -e ...`
- Build image: `docker build -t flask-app .`
- Start web container with all flags: `docker run -d --name flask-app --network class-net -p 8000:7000 -e ...`
- **Result**: 30+ lines of shell script, easy to make mistakes, hard to maintain

### The New Way (Docker Compose)
- One file: `docker-compose.yml`
- One command: `docker-compose up`
- **Result**: Clean, declarative, version-controlled configuration

## Key Benefits

1. **Automatic Network Creation**: No need for `docker network create` - Compose handles it
2. **Service Discovery**: Services can find each other by name (e.g., `db` instead of IP addresses)
3. **Dependency Management**: `depends_on` ensures correct startup order
4. **Volume Management**: Named volumes persist data automatically
5. **Single Command**: Start everything with `docker-compose up`

## How to Run

1. **Start the application:**
   ```bash
   docker-compose up
   ```

2. **Start in detached mode (background):**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs
   ```

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

5. **Stop and remove volumes (clean slate):**
   ```bash
   docker-compose down -v
   ```

6. **Rebuild after code changes:**
   ```bash
   docker-compose up --build
   ```

## Access the Application

Once running, access the Flask app at: http://localhost:8000

You should see: `Connected to DB!`

## Check Your Understanding

**Question**: In the manual script, we had to run `docker network create class-net`. Where did that command go in Docker Compose?

**Answer**: Docker Compose automatically creates networks defined in the `networks:` section. You don't need to manually create them - Compose handles network creation, service discovery, and DNS resolution automatically when you run `docker-compose up`.

## What Happens Behind the Scenes

When you run `docker-compose up`, Docker Compose:
1. Creates the network `docker_compose_lab2_app-network` (prefixed with project name)
2. Creates the volume `docker_compose_lab2_postgres-data`
3. Starts the `db` service first (because `web` depends on it)
4. Starts the `web` service
5. Sets up DNS so `web` can resolve `db` as a hostname

All of this happens automatically - no manual commands needed!
