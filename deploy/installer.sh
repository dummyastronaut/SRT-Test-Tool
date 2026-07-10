#!/bin/bash
set -e

# Create system user
sudo useradd -r -s /bin/false srt-monitor || true

# Create directories
sudo mkdir -p /opt/srt-monitor/app \
             /opt/srt-monitor/static \
             /var/lib/srt-monitor \
             /var/log/srt-monitor \
             /opt/srt-monitor/data/configs \
             /opt/srt-monitor/data/reports

# Set permissions
sudo chown -R srt-monitor:srt-monitor /opt/srt-monitor /var/lib/srt-monitor /var/log/srt-monitor
sudo chmod -R 755 /opt/srt-monitor

# Install Python dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv iperf3

# Create virtual environment
sudo -u srt-monitor python3 -m venv /opt/srt-monitor/venv

# Install Python packages
sudo -u srt-monitor /opt/srt-monitor/venv/bin/pip install --upgrade pip
sudo -u srt-monitor /opt/srt-monitor/venv/bin/pip install -r /opt/srt-monitor/app/requirements.txt

# Install systemd service
sudo bash -c 'cat > /etc/systemd/system/srt-monitor.service << "EOF"
[Unit]
Description=SRT Monitor Service
After=network.target

[Service]
User=srt-monitor
Group=srt-monitor
WorkingDirectory=/opt/srt-monitor/app
Environment="PATH=/opt/srt-monitor/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/srt-monitor/venv/bin/python3 /opt/srt-monitor/app/app.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/srt-monitor/service.log
StandardError=append:/var/log/srt-monitor/service-error.log

[Install]
WantedBy=multi-user.target
EOF'

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable srt-monitor
sudo systemctl start srt-monitor

echo "✅ Installation complete!"
echo "🌐 Access the web interface at: http://localhost:5001"
echo "📊 Service status: sudo systemctl status srt-monitor"
