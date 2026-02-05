"""
Top Secret Dashboard - Spy Agency Edition
Reads MISSION_NAME (ConfigMap) and ACCESS_CODE (Secret) from environment variables.
"""
import os
from flask import Flask

app = Flask(__name__)


@app.route('/')
def dashboard():
    mission_name = os.getenv('MISSION_NAME', 'Configuration Missing!')
    access_code = os.getenv('ACCESS_CODE', 'Configuration Missing!')

    return f"""
    <h1>Mission: {mission_name}</h1>
    <p>Secret Code: {access_code}</p>
    """


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
