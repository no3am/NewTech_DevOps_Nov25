# Metric app for Prometheus Pull Model lab
FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir prometheus_client

COPY main.py .

CMD ["python", "main.py"]
