import socket
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    hostname = socket.gethostname()
    return f"Hello! I am Container ID: {hostname}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
