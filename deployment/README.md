# VPS Deployment Files

This folder contains everything you need to deploy the Discord Data Scraper on your Ubuntu VPS.

## Files

- **install_vps.sh** - Automated installation script
- **discord-scraper.service** - Systemd service file
- **nginx.conf** - Nginx reverse proxy configuration

## Quick Start

### Automated Installation (Easiest)

1. Upload the entire DCSC project to your VPS:
```bash
# On your local machine
scp -r DCSC user@your-vps-ip:/home/user/

# Or clone from git
ssh user@your-vps-ip
git clone YOUR_REPO_URL DCSC
cd DCSC
```

2. Run the installation script:
```bash
cd DCSC/deployment
chmod +x install_vps.sh
./install_vps.sh
```

The script will:
- Install all dependencies
- Setup Python virtual environment
- Create systemd service
- Configure Nginx (optional)
- Setup firewall
- Start the service

### Manual Installation

See [DEPLOYMENT.md](../DEPLOYMENT.md) in the parent directory for detailed manual installation instructions.

## Access Your Scraper

After installation:

**With Nginx:**
- HTTP: `http://your-domain.com` or `http://YOUR_VPS_IP`
- HTTPS: `https://your-domain.com` (after SSL setup)

**Without Nginx (direct):**
- `http://YOUR_VPS_IP:5000`

## Managing the Service

```bash
# Start
sudo systemctl start discord-scraper

# Stop
sudo systemctl stop discord-scraper

# Restart
sudo systemctl restart discord-scraper

# Status
sudo systemctl status discord-scraper

# Logs
sudo journalctl -u discord-scraper -f
```

## SSL Setup (HTTPS)

After installation, setup free SSL with Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Certbot will automatically:
- Get SSL certificate
- Configure Nginx for HTTPS
- Setup auto-renewal

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u discord-scraper -n 50

# Check if port is in use
sudo netstat -tulpn | grep 5000
```

### Can't access from browser
```bash
# Check firewall
sudo ufw status

# Allow nginx
sudo ufw allow 'Nginx Full'

# Or allow direct access
sudo ufw allow 5000
```

### Nginx errors
```bash
# Test configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log
```

## Security

**Important:** For production use:

1. Setup SSL/HTTPS (see above)
2. Add authentication (see DEPLOYMENT.md)
3. Keep system updated: `sudo apt update && sudo apt upgrade`
4. Use strong passwords
5. Configure firewall properly

## Need Help?

See the main [DEPLOYMENT.md](../DEPLOYMENT.md) for comprehensive documentation.
