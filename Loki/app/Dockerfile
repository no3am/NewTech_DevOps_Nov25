# Payment Processor for 'The Poison Pill' Loki lab
FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir flask prometheus_client

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
