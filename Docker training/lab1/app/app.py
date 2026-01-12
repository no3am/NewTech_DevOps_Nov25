"""
Simple Flask Web Application
A basic web app for Docker containerization practice
"""

from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)


@app.route("/")
def home():
    """Welcome page"""
    return """
    <html>
        <head>
            <title>Docker Lab 1 - Web App</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                h1 {{
                    color: #333;
                }}
                .info {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .endpoint {{
                    margin: 10px 0;
                    padding: 10px;
                    background-color: #e8f4f8;
                    border-left: 4px solid #2196F3;
                }}
            </style>
        </head>
        <body>
            <div class="info">
                <h1>🐳 Welcome to Docker Lab 1!</h1>
                <p>Congratulations! Your containerized application is running successfully.</p>
                <p><strong>Current Time:</strong> {}</p>
                <h2>Available Endpoints:</h2>
                <div class="endpoint">
                    <strong>GET /</strong> - This welcome page
                </div>
                <div class="endpoint">
                    <strong>GET /api/time</strong> - Get current time as JSON
                </div>
                <div class="endpoint">
                    <strong>GET /api/health</strong> - Health check endpoint
                </div>
            </div>
        </body>
    </html>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@app.route("/api/time")
def get_time():
    """API endpoint to get current time"""
    return jsonify(
        {
            "timestamp": datetime.now().isoformat(),
            "message": "Current server time",
            "status": "success",
        }
    )


@app.route("/api/health")
def health():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "service": "web-app",
            "timestamp": datetime.now().isoformat(),
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting web application on {host}:{port}")
    app.run(host=host, port=port, debug=False)
