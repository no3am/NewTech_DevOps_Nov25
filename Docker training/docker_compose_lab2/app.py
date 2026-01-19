import os
from flask import Flask
import psycopg2

app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Docker Compose automatically creates a network and DNS entries
        # The service name 'db' in docker-compose.yml becomes a hostname
        # This is Docker's built-in service discovery - no need for IP addresses!
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'db'),  # 'db' matches the service name in docker-compose.yml
            database=os.getenv('DB_NAME', 'mydb'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            port=os.getenv('DB_PORT', '5432')
        )
        conn.close()
        return 'Connected to DB!'
    except Exception as e:
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
