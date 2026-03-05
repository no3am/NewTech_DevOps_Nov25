# Chain Reaction: 3-tier microservices (Service-A, B, C)
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
# Override CMD in Deployment: python service_a.py | service_b.py | service_c.py
CMD ["python", "service_a.py"]
