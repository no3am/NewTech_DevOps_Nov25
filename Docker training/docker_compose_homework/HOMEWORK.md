# Homework Assignment: Containerizing "The Guestbook" Application

## Scenario

You are a DevOps engineer. The development team has finished writing a Python Flask application called **"The Guestbook"** - a simple web service that allows users to sign a guestbook and read messages.

However, the developers don't know Docker. They've handed you the source code and said: *"Make it run in containers, please!"*

Your job is to containerize this application and set up the necessary infrastructure.

## The Application

**The Guestbook** is a Flask REST API with two main endpoints:

- `POST /sign` - Add a message to the guestbook
  - Request body: `{"message": "Hello, World!"}`
  - Returns: The created message with ID

- `GET /messages` - Retrieve all messages
  - Returns: List of all messages in reverse chronological order

- `GET /health` - Health check endpoint (useful for debugging)

The application connects to a PostgreSQL database to store messages. It uses environment variables for database configuration:
- `DB_HOST` - Database hostname
- `DB_NAME` - Database name
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_PORT` - Database port (defaults to 5432)

**Important**: The application will crash on startup if it cannot connect to the database. This is intentional - it helps you debug connection issues!

## Your Mission

Create the Docker infrastructure needed to run this application. You must complete the following requirements:

### Requirement 1: Create a Dockerfile

Write a `Dockerfile` for the Python Flask application.

**Considerations:**
- Choose an appropriate base image (Python version?)
- Set the working directory
- Install dependencies from `requirements.txt`
- Copy the application code
- Expose the correct port (check `app.py` to see what port it uses)
- Define the command to run the application

**Hint**: The app runs on port 5000 by default.

### Requirement 2: Create docker-compose.yml

Write a `docker-compose.yml` file that orchestrates:
- The Flask application service
- A PostgreSQL database service

**Considerations:**
- What base image should you use for PostgreSQL?
- What port should the Flask app be accessible on from your host machine?
- How will the services communicate? (Hint: Docker Compose creates a network automatically)

### Requirement 3: Configure Networking and Environment Variables

The Flask app needs to connect to the database. You must:

- Set up environment variables so the app can find the database
- Ensure both services are on the same network (Docker Compose handles this automatically)
- Use the service name as the hostname (e.g., if your service is named `db`, use `db` as `DB_HOST`)

**Hint**: Look at `app.py` to see exactly which environment variables it expects!

### Requirement 4: Ensure Data Persistence

Messages stored in the database should **not disappear** when containers are stopped and restarted.

- Configure a volume for PostgreSQL data
- Use a named volume (Docker Compose will manage it)
- PostgreSQL stores its data in `/var/lib/postgresql/data` inside the container

## Testing Your Solution

Once you've created your `Dockerfile` and `docker-compose.yml`:

1. **Start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Test adding a message:**
   ```bash
   curl -X POST http://localhost:5000/sign \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello from Docker!"}'
   ```

3. **Test retrieving messages:**
   ```bash
   curl http://localhost:5000/messages
   ```

4. **Test persistence:**
   - Stop containers: `docker-compose down`
   - Start again: `docker-compose up`
   - Check messages: `curl http://localhost:5000/messages`
   - Your previous message should still be there!

5. **Check health:**
   ```bash
   curl http://localhost:5000/health
   ```

## Deliverables

Submit the following files:

1. `Dockerfile` - Your containerized Flask application
2. `docker-compose.yml` - Your multi-container orchestration file
3. **Screenshot** showing:
   - Successful `docker-compose up` output
   - At least one message added via `POST /sign`
   - Messages retrieved via `GET /messages`
   - Health check showing database connected

## Common Issues & Debugging Tips

- **Application crashes on startup**: Check your environment variables match what `app.py` expects
- **Cannot connect to database**: Verify service names match in `docker-compose.yml` and environment variables
- **Port already in use**: Change the host port mapping in `docker-compose.yml`
- **Data disappears after restart**: You forgot to add a volume for PostgreSQL!

## Grading Criteria

- **Dockerfile** (30%): Correctly builds and runs the Flask app
- **docker-compose.yml** (40%): Properly orchestrates both services with correct configuration
- **Environment Variables** (15%): App successfully connects to database
- **Data Persistence** (15%): Messages survive container restarts

## Bonus Challenge (Optional)

- Add a `README.md` explaining how to run your solution
- Add environment variable files (`.env`) for configuration
- Implement proper error handling in your Dockerfile (health checks)
- Add a third service: Redis for caching (if you're feeling ambitious!)

Good luck! 🐳
