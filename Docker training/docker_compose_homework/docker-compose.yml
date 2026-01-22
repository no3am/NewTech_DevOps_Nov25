version: '3.8'

services:
  # PostgreSQL Database Service
  db:
    image: postgres:15-alpine
    container_name: guestbook_db
    environment:
      POSTGRES_DB: guestbook
      POSTGRES_USER: guestbook_user
      POSTGRES_PASSWORD: guestbook_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U guestbook_user -d guestbook"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Flask Application Service
  app:
    build: .
    container_name: guestbook_app
    environment:
      DB_HOST: db
      DB_NAME: guestbook
      DB_USER: guestbook_user
      DB_PASSWORD: guestbook_password
      DB_PORT: 5432
    ports:
      - "5000:5000"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

# Named volume for PostgreSQL data persistence
volumes:
  postgres_data:
