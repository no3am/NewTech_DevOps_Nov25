"""
Whoami - A simple Flask app that returns the Pod hostname.
Used in Kubernetes lab to demonstrate Service load balancing.
"""
import socket
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    hostname = socket.gethostname()
    return f"Request served by Pod: {hostname}\n"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
