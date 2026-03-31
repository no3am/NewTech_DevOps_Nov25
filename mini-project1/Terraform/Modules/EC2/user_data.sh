#!/bin/bash

apt-get update -y
apt-get upgrade -y

# Install Python 3 (whatever version Ubuntu 24.04 has, which is 3.12)
apt-get install -y python3 python3-pip python3-venv git

mkdir -p /home/ubuntu/flask-app
cd /home/ubuntu/flask-app

git clone https://github.com/bahjatnsasra/NewTech_DevOps_Nov25.git .

cd mini-project1

# Remove the empty minienv from repo and create a proper one
rm -rf minienv
python3 -m venv minienv

# Now activate it
source minienv/bin/activate

cd app
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

cat > /etc/systemd/system/flaskapp.service <<EOF
[Unit]
Description=Gunicorn service for Flask app
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/flask-app/mini-project1/app
Environment="PATH=/home/ubuntu/flask-app/mini-project1/minienv/bin"
ExecStart=/home/ubuntu/flask-app/mini-project1/minienv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 main:app

[Install]
WantedBy=multi-user.target
EOF

chown -R ubuntu:ubuntu /home/ubuntu/flask-app

systemctl daemon-reload
systemctl enable flaskapp
systemctl start flaskapp