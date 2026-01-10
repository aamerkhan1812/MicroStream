#!/bin/bash
# Oracle Cloud Free Tier Deployment Script
# Deploys MicroStream to Oracle Cloud Always Free VM

set -e

echo "============================================================"
echo "MicroStream - Oracle Cloud Free Deployment"
echo "============================================================"

# Update system
echo "[1/8] Updating system..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker
echo "[2/8] Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

# Install Docker Compose
echo "[3/8] Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository (or copy files)
echo "[4/8] Setting up project..."
cd ~
if [ ! -d "MicroStream" ]; then
    mkdir -p MicroStream
fi
cd MicroStream

# Copy your files here (you'll upload via SCP)
# For now, we'll assume files are already here

# Configure firewall
echo "[5/8] Configuring firewall..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8501 -j ACCEPT
sudo netfilter-persistent save

# Set up systemd service for auto-restart
echo "[6/8] Creating systemd service..."
sudo tee /etc/systemd/system/microstream.service > /dev/null <<EOF
[Unit]
Description=MicroStream Real-Time Market Analysis
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/MicroStream
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ubuntu

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable microstream.service

# Start services
echo "[7/8] Starting MicroStream..."
docker-compose up -d

# Show status
echo "[8/8] Deployment complete!"
echo ""
echo "============================================================"
echo "MicroStream is now running 24/7!"
echo "============================================================"
echo ""
echo "Access dashboard at: http://$(curl -s ifconfig.me):8501"
echo ""
echo "Useful commands:"
echo "  Status:  sudo systemctl status microstream"
echo "  Logs:    docker-compose logs -f"
echo "  Restart: sudo systemctl restart microstream"
echo ""
