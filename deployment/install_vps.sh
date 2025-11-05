#!/bin/bash

# Discord Data Scraper - VPS Installation Script
# This script automates the installation on Ubuntu VPS

set -e  # Exit on error

echo "=========================================="
echo "Discord Data Scraper - VPS Installation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root"
    echo "Run as regular user with sudo privileges"
    exit 1
fi

# Get username
USERNAME=$(whoami)
INSTALL_DIR="/home/$USERNAME/DCSC"

echo "Installation will be done in: $INSTALL_DIR"
echo "Username: $USERNAME"
echo ""

# Confirm
read -p "Continue with installation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 1
fi

echo ""
echo "Step 1: Updating system..."
sudo apt update
sudo apt upgrade -y

echo ""
echo "Step 2: Installing dependencies..."
sudo apt install -y python3 python3-pip python3-venv git nginx

echo ""
echo "Step 3: Creating directory and setting up project..."
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Project directory not found. Please upload/clone the project first to $INSTALL_DIR"
    exit 1
fi

cd "$INSTALL_DIR"

echo ""
echo "Step 4: Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Step 5: Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Step 6: Creating output directory..."
mkdir -p output

echo ""
echo "Step 7: Setting up systemd service..."

# Create service file
sudo tee /etc/systemd/system/discord-scraper.service > /dev/null <<EOF
[Unit]
Description=Discord Data Scraper Web Interface
After=network.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python app.py
Restart=always
RestartSec=10

StandardOutput=append:$INSTALL_DIR/scraper.log
StandardError=append:$INSTALL_DIR/scraper.error.log

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable discord-scraper

echo ""
echo "Step 8: Configuring Nginx..."

# Ask if user wants nginx setup
read -p "Setup Nginx reverse proxy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your domain name (or press Enter to use IP): " DOMAIN

    if [ -z "$DOMAIN" ]; then
        DOMAIN="_"  # Default server
    fi

    # Create nginx config
    sudo tee /etc/nginx/sites-available/discord-scraper > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    proxy_read_timeout 3600;
    proxy_connect_timeout 3600;
    proxy_send_timeout 3600;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_buffering off;
    }

    client_max_body_size 10M;
}
EOF

    # Enable site
    sudo ln -sf /etc/nginx/sites-available/discord-scraper /etc/nginx/sites-enabled/

    # Remove default site if exists
    sudo rm -f /etc/nginx/sites-enabled/default

    # Test nginx config
    sudo nginx -t

    # Reload nginx
    sudo systemctl reload nginx

    echo "Nginx configured successfully!"
fi

echo ""
echo "Step 9: Configuring Firewall..."

# Check if ufw is active
if sudo ufw status | grep -q "Status: active"; then
    echo "UFW is active, configuring..."
    sudo ufw allow 'Nginx Full'
    sudo ufw allow OpenSSH
else
    echo "UFW is not active. Configure manually if needed."
fi

echo ""
echo "Step 10: Starting the service..."
sudo systemctl start discord-scraper

# Wait a moment
sleep 2

# Check status
if sudo systemctl is-active --quiet discord-scraper; then
    echo "Service started successfully!"
else
    echo "Warning: Service may not have started correctly"
    echo "Check status with: sudo systemctl status discord-scraper"
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Service Status:"
sudo systemctl status discord-scraper --no-pager
echo ""
echo "Access your scraper at:"
if [ "$DOMAIN" != "_" ] && [ -n "$DOMAIN" ]; then
    echo "  http://$DOMAIN"
else
    VPS_IP=$(hostname -I | awk '{print $1}')
    echo "  http://$VPS_IP"
fi
echo ""
echo "Useful commands:"
echo "  Start:   sudo systemctl start discord-scraper"
echo "  Stop:    sudo systemctl stop discord-scraper"
echo "  Restart: sudo systemctl restart discord-scraper"
echo "  Logs:    sudo journalctl -u discord-scraper -f"
echo ""
echo "To setup SSL (HTTPS):"
echo "  sudo apt install certbot python3-certbot-nginx"
echo "  sudo certbot --nginx -d yourdomain.com"
echo ""
echo "=========================================="
