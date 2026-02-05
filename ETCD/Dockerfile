FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY watcher.py .

# Run the watcher with unbuffered output
ENV PYTHONUNBUFFERED=1
CMD ["python", "-u", "watcher.py"]
