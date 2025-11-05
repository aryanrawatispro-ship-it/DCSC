# VPS Deployment Guide

This guide will help you deploy the Discord Data Scraper web interface on your Ubuntu VPS.

## Prerequisites

- Ubuntu VPS (18.04, 20.04, 22.04, or newer)
- Root or sudo access
- Domain name (optional, but recommended)
- SSH access to your VPS

## Quick Installation

### 1. Connect to Your VPS

```bash
ssh user@your-vps-ip
```

### 2. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Install Python and Dependencies

```bash
# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv git -y

# Install nginx (for reverse proxy)
sudo apt install nginx -y
```

### 4. Clone or Upload Your Project

**Option A: Using Git (Recommended)**
```bash
cd /home/$USER
git clone https://github.com/your-username/DCSC.git
cd DCSC
```

**Option B: Upload Files**
```bash
# On your local machine
scp -r DCSC user@your-vps-ip:/home/user/

# Then on VPS
cd /home/$USER/DCSC
```

### 5. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Test the Application

```bash
# Run the app
python app.py
```

You should see:
```
Discord Data Scraper - Web Interface
Starting web server...
Open your browser and navigate to: http://localhost:5000
```

Press `Ctrl+C` to stop it.

## Production Deployment

### Option 1: Simple (Direct Access via IP)

If you just want quick access via IP address:

```bash
# Edit app.py to change host (already done - it's set to 0.0.0.0)
# Open firewall
sudo ufw allow 5000

# Run in background with nohup
nohup python3 app.py > scraper.log 2>&1 &

# Check if it's running
ps aux | grep app.py
```

Access at: `http://YOUR_VPS_IP:5000`

### Option 2: Production Setup (Systemd + Nginx + Domain)

This is the **recommended** approach for production.

#### Step 1: Create Systemd Service

Create `/etc/systemd/system/discord-scraper.service`:

```bash
sudo nano /etc/systemd/system/discord-scraper.service
```

Paste this content (see discord-scraper.service file in deployment folder).

#### Step 2: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable discord-scraper

# Start service
sudo systemctl start discord-scraper

# Check status
sudo systemctl status discord-scraper
```

#### Step 3: Setup Nginx Reverse Proxy

Create nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/discord-scraper
```

Paste nginx configuration (see nginx.conf file in deployment folder).

Enable the site:

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/discord-scraper /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

#### Step 4: Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Allow SSH (important!)
sudo ufw allow OpenSSH

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

Now access at: `http://your-domain.com` or `http://YOUR_VPS_IP`

### Option 3: With SSL (HTTPS) - Free with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certbot will automatically configure nginx for HTTPS
```

Now access securely at: `https://yourdomain.com`

## Managing the Service

```bash
# Start
sudo systemctl start discord-scraper

# Stop
sudo systemctl stop discord-scraper

# Restart
sudo systemctl restart discord-scraper

# View logs
sudo journalctl -u discord-scraper -f

# Check status
sudo systemctl status discord-scraper
```

## Updating the Application

```bash
# Navigate to project directory
cd /home/$USER/DCSC

# Activate virtual environment
source venv/bin/activate

# Pull latest changes (if using git)
git pull

# Install any new dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart discord-scraper
```

## Troubleshooting

### Check if service is running
```bash
sudo systemctl status discord-scraper
ps aux | grep app.py
```

### View logs
```bash
# Systemd logs
sudo journalctl -u discord-scraper -n 50

# Application logs
tail -f /home/$USER/DCSC/scraper.log
```

### Check ports
```bash
sudo netstat -tulpn | grep 5000
```

### Test nginx configuration
```bash
sudo nginx -t
```

### Firewall issues
```bash
sudo ufw status
sudo ufw allow 5000  # For direct access
sudo ufw allow 'Nginx Full'  # For nginx
```

## Security Recommendations

1. **Change Default Port** - Edit `app.py` to use a non-standard port
2. **Use HTTPS** - Always use SSL in production (Let's Encrypt is free)
3. **Firewall** - Only open necessary ports
4. **Keep Updated** - Regularly update system and dependencies
5. **Strong Passwords** - Use strong SSH passwords or key-based auth
6. **Backup** - Regularly backup your scraped data
7. **Rate Limiting** - Consider adding rate limiting to the web interface
8. **Authentication** - For production, add user authentication

## Optional: Add Basic Authentication

If you want to protect your web interface with a password:

```bash
# Install apache2-utils
sudo apt install apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd yourusername

# Add to nginx configuration (in location block):
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;

# Reload nginx
sudo systemctl reload nginx
```

## Performance Optimization

### For High-Volume Scraping

Edit `/etc/systemd/system/discord-scraper.service` and add:

```ini
[Service]
Environment="EVENTLET_THREADPOOL_SIZE=20"
```

### Increase System Limits

```bash
# Edit limits.conf
sudo nano /etc/security/limits.conf

# Add these lines:
* soft nofile 65536
* hard nofile 65536
```

## Monitoring

### Install htop for system monitoring
```bash
sudo apt install htop
htop
```

### Monitor disk space
```bash
df -h
du -sh /home/$USER/DCSC/output/
```

### Monitor service
```bash
watch -n 1 'systemctl status discord-scraper'
```

## Backup

```bash
# Backup output folder
tar -czf discord-scraper-backup-$(date +%Y%m%d).tar.gz output/

# Backup to remote location
scp discord-scraper-backup-*.tar.gz user@backup-server:/backups/
```

## Quick Reference Commands

```bash
# Start service
sudo systemctl start discord-scraper

# Stop service
sudo systemctl stop discord-scraper

# Restart service
sudo systemctl restart discord-scraper

# View logs
sudo journalctl -u discord-scraper -f

# Check nginx
sudo nginx -t
sudo systemctl reload nginx

# Firewall
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443
```

## URLs After Setup

- **Direct Access**: `http://YOUR_VPS_IP:5000`
- **With Nginx**: `http://YOUR_VPS_IP` or `http://yourdomain.com`
- **With SSL**: `https://yourdomain.com`

## Need Help?

Common issues:

1. **Port already in use**: Change port in `app.py`
2. **Permission denied**: Use `sudo` or fix file permissions
3. **Can't access externally**: Check firewall and VPS security groups
4. **Service won't start**: Check logs with `journalctl -u discord-scraper`
