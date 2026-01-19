#!/bin/bash

set -e

echo "Creating docker network..."
docker network create class-net

echo "Starting PostgreSQL container..."
docker run -d \
  --name postgres-db \
  --network class-net \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres123 \
  -e POSTGRES_DB=mydb \
  postgres:15

echo "Waiting for PostgreSQL to be ready..."
sleep 5

echo "Building Flask image..."
docker build -t flask-app .

echo "Running Flask container..."
docker run -d \
  --name flask-app \
  --network class-net \
  -p 8000:7000 \
  -e DB_HOST=postgres-db \
  -e DB_NAME=mydb \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres123 \
  -e DB_PORT=5432 \
  flask-app

echo "Deployment complete!"
echo "Access the app at http://localhost:8000"
