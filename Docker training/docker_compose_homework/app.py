import os
from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

def get_db_connection():
    """Connect to PostgreSQL database using environment variables."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {str(e)}")
        print(f"DB_HOST: {os.getenv('DB_HOST')}")
        print(f"DB_NAME: {os.getenv('DB_NAME')}")
        print(f"DB_USER: {os.getenv('DB_USER')}")
        raise

def init_db():
    """Initialize the database table if it doesn't exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/sign', methods=['POST'])
def sign_guestbook():
    """Add a message to the guestbook."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message field'}), 400
        
        message = data['message']
        if not message.strip():
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO messages (message) VALUES (%s) RETURNING id', (message,))
        message_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'id': message_id, 'message': message, 'status': 'success'}), 201
    except Exception as e:
        print(f"ERROR in /sign: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/messages', methods=['GET'])
def get_messages():
    """Retrieve all messages from the guestbook."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, message, created_at FROM messages ORDER BY created_at DESC')
        messages = cur.fetchall()
        cur.close()
        conn.close()
        
        result = [
            {
                'id': msg[0],
                'message': msg[1],
                'created_at': str(msg[2])
            }
            for msg in messages
        ]
        
        return jsonify({'messages': result, 'count': len(result)}), 200
    except Exception as e:
        print(f"ERROR in /messages: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify database connectivity."""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

if __name__ == '__main__':
    print("Starting The Guestbook application...")
    print("Attempting to connect to database...")
    try:
        init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"FATAL ERROR: Cannot initialize database: {str(e)}")
        print("Application will crash. Please check your database configuration.")
        raise
    
    app.run(host='0.0.0.0', port=5000, debug=True)
