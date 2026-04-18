# Digital Ocean Deployment Guide - Backend

## Overview

Deploy your Fridge Observer backend to Digital Ocean for production use. This guide covers droplet setup, environment configuration, and continuous deployment.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION SETUP                         │
└─────────────────────────────────────────────────────────────┘

Vercel (Frontend)          Digital Ocean (Backend)
     │                            │
     │ HTTPS                      │
     └──────────► API ◄───────────┘
                  │
                  ├─ FastAPI Server
                  ├─ Supabase Database
                  ├─ Gemini AI
                  └─ Replicate API

Raspberry Pi ──WiFi──► Digital Ocean API
```

## Prerequisites

- [ ] Digital Ocean account
- [ ] Domain name (optional but recommended)
- [ ] GitHub repository
- [ ] API keys (Gemini, Replicate, Supabase)

## Step 1: Create Digital Ocean Droplet (10 minutes)

### 1.1 Create Droplet

1. Log in to [Digital Ocean](https://cloud.digitalocean.com/)
2. Click **Create** → **Droplets**
3. Choose configuration:

**Image**: Ubuntu 22.04 LTS
**Plan**: Basic
**CPU Options**: Regular (2 GB RAM / 1 CPU) - $12/month
**Datacenter**: Choose closest to you (e.g., New York, San Francisco)
**Authentication**: SSH Key (recommended) or Password
**Hostname**: `fridge-observer-api`

4. Click **Create Droplet**
5. Wait 1-2 minutes for creation
6. Note the IP address (e.g., `164.90.xxx.xxx`)

### 1.2 Initial Server Setup

SSH into your droplet:

```bash
ssh root@YOUR_DROPLET_IP
```

Update system:

```bash
apt update && apt upgrade -y
```

Create non-root user:

```bash
adduser fridge
usermod -aG sudo fridge
```

Setup SSH for new user:

```bash
rsync --archive --chown=fridge:fridge ~/.ssh /home/fridge
```

Switch to new user:

```bash
su - fridge
```

## Step 2: Install Dependencies (15 minutes)

### 2.1 Install Python 3.11

```bash
sudo apt install -y python3.11 python3.11-venv python3-pip
```

### 2.2 Install PostgreSQL (for local development/testing)

```bash
sudo apt install -y postgresql postgresql-contrib
```

### 2.3 Install Nginx (reverse proxy)

```bash
sudo apt install -y nginx
```

### 2.4 Install Certbot (SSL certificates)

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2.5 Install Git

```bash
sudo apt install -y git
```

## Step 3: Clone Repository (5 minutes)

### 3.1 Clone Your Repo

```bash
cd /home/fridge
git clone https://github.com/YOUR_USERNAME/fridge-observer.git
cd fridge-observer
```

### 3.2 Create Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3.3 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Configure Environment (10 minutes)

### 4.1 Create Production .env File

```bash
nano .env
```

Add:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# AI APIs
GEMINI_API_KEY=your_gemini_api_key
K2_API_KEY=your_k2_api_key

# Image Generation
REPLICATE_API_TOKEN=your_replicate_token

# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production

# Security
SECRET_KEY=your_super_secret_key_here_generate_with_openssl
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://www.yourdomain.com

# CORS
CORS_ORIGINS=["https://your-frontend.vercel.app","https://www.yourdomain.com"]
```

**Generate SECRET_KEY:**

```bash
openssl rand -hex 32
```

Save and exit: **Ctrl+X**, **Y**, **Enter**

### 4.2 Set Permissions

```bash
chmod 600 .env
```

## Step 5: Setup Systemd Service (10 minutes)

### 5.1 Create Service File

```bash
sudo nano /etc/systemd/system/fridge-observer.service
```

Add:

```ini
[Unit]
Description=Fridge Observer API
After=network.target

[Service]
Type=simple
User=fridge
Group=fridge
WorkingDirectory=/home/fridge/fridge-observer
Environment="PATH=/home/fridge/fridge-observer/.venv/bin"
ExecStart=/home/fridge/fridge-observer/.venv/bin/uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.2 Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable fridge-observer
sudo systemctl start fridge-observer
```

### 5.3 Check Status

```bash
sudo systemctl status fridge-observer
```

Should show: **Active: active (running)**

### 5.4 View Logs

```bash
sudo journalctl -u fridge-observer -f
```

## Step 6: Configure Nginx (15 minutes)

### 6.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/fridge-observer
```

Add:

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN.com www.YOUR_DOMAIN.com;

    # Increase upload size for images
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_read_timeout 86400;
    }

    # WebSocket endpoint
    location /ws {
        proxy_pass http://127.0.0.1:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

**If you don't have a domain yet**, use IP address:

```nginx
server {
    listen 80;
    server_name YOUR_DROPLET_IP;
    
    # ... rest of config same as above
}
```

### 6.2 Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/fridge-observer /etc/nginx/sites-enabled/
```

### 6.3 Test Configuration

```bash
sudo nginx -t
```

Should show: **syntax is ok**

### 6.4 Restart Nginx

```bash
sudo systemctl restart nginx
```

## Step 7: Setup SSL with Let's Encrypt (5 minutes)

**Only if you have a domain name:**

### 7.1 Point Domain to Droplet

In your domain registrar (Namecheap, GoDaddy, etc.):

1. Add **A Record**: `@` → `YOUR_DROPLET_IP`
2. Add **A Record**: `www` → `YOUR_DROPLET_IP`
3. Wait 5-10 minutes for DNS propagation

### 7.2 Get SSL Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow prompts:
- Enter email
- Agree to terms
- Choose: **Redirect HTTP to HTTPS** (option 2)

### 7.3 Test Auto-Renewal

```bash
sudo certbot renew --dry-run
```

## Step 8: Configure Firewall (5 minutes)

### 8.1 Setup UFW

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 8.2 Check Status

```bash
sudo ufw status
```

Should show:
```
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
Nginx Full                 ALLOW       Anywhere
```

## Step 9: Test Deployment (5 minutes)

### 9.1 Test API

```bash
curl http://YOUR_DOMAIN.com/api/health
# or
curl http://YOUR_DROPLET_IP/api/health
```

Should return: `{"status":"ok"}`

### 9.2 Test from Browser

Open: `https://YOUR_DOMAIN.com` (or `http://YOUR_DROPLET_IP`)

Should see API documentation or redirect to login.

### 9.3 Test WebSocket

```bash
# Install wscat
npm install -g wscat

# Test WebSocket
wscat -c wss://YOUR_DOMAIN.com/ws
# or
wscat -c ws://YOUR_DROPLET_IP/ws
```

## Step 10: Update Raspberry Pi Configuration (5 minutes)

On your Raspberry Pi, update `.env`:

```bash
nano ~/fridge-observer/.env
```

Change:

```env
API_BASE_URL=https://YOUR_DOMAIN.com
# or
API_BASE_URL=http://YOUR_DROPLET_IP
```

Restart sensor:

```bash
sudo systemctl restart fridge-observer
```

## Continuous Deployment

### Option 1: Manual Deployment

```bash
# SSH into droplet
ssh fridge@YOUR_DROPLET_IP

# Pull latest code
cd /home/fridge/fridge-observer
git pull origin main

# Install new dependencies (if any)
source .venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart fridge-observer
```

### Option 2: Automated with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Digital Ocean

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Digital Ocean
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DO_HOST }}
          username: ${{ secrets.DO_USERNAME }}
          key: ${{ secrets.DO_SSH_KEY }}
          script: |
            cd /home/fridge/fridge-observer
            git pull origin main
            source .venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart fridge-observer
```

Add secrets in GitHub:
- `DO_HOST`: Your droplet IP
- `DO_USERNAME`: `fridge`
- `DO_SSH_KEY`: Your private SSH key

## Monitoring

### Check Service Status

```bash
sudo systemctl status fridge-observer
```

### View Logs

```bash
# Real-time logs
sudo journalctl -u fridge-observer -f

# Last 100 lines
sudo journalctl -u fridge-observer -n 100

# Logs from today
sudo journalctl -u fridge-observer --since today
```

### Check Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### Monitor Resources

```bash
# CPU and memory
htop

# Disk usage
df -h

# Network
sudo netstat -tulpn | grep :8000
```

## Backup Strategy

### Database Backup (if using local PostgreSQL)

```bash
# Create backup script
nano ~/backup.sh
```

Add:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump fridge_observer > /home/fridge/backups/db_$DATE.sql
# Keep only last 7 days
find /home/fridge/backups -name "db_*.sql" -mtime +7 -delete
```

Make executable:

```bash
chmod +x ~/backup.sh
```

Add to crontab:

```bash
crontab -e
```

Add:

```
0 2 * * * /home/fridge/backup.sh
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u fridge-observer -n 50

# Check if port is in use
sudo netstat -tulpn | grep :8000

# Test manually
cd /home/fridge/fridge-observer
source .venv/bin/activate
uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8000
```

### Nginx 502 Bad Gateway

```bash
# Check if service is running
sudo systemctl status fridge-observer

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Restart both
sudo systemctl restart fridge-observer
sudo systemctl restart nginx
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

### High Memory Usage

```bash
# Check memory
free -h

# Restart service
sudo systemctl restart fridge-observer

# Consider upgrading droplet
```

## Security Best Practices

1. ✅ Use SSH keys, not passwords
2. ✅ Enable firewall (UFW)
3. ✅ Use SSL/HTTPS
4. ✅ Keep system updated: `sudo apt update && sudo apt upgrade`
5. ✅ Use strong SECRET_KEY
6. ✅ Restrict CORS origins
7. ✅ Regular backups
8. ✅ Monitor logs

## Cost Estimate

- **Droplet**: $12/month (2GB RAM)
- **Domain**: $10-15/year (optional)
- **Total**: ~$12-13/month

## Performance Optimization

### Enable Gzip Compression

Edit Nginx config:

```bash
sudo nano /etc/nginx/nginx.conf
```

Add in `http` block:

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

### Add Caching

In Nginx site config:

```nginx
location /static {
    alias /home/fridge/fridge-observer/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## Next Steps

1. ✅ Deploy backend to Digital Ocean
2. ⏳ Deploy frontend to Vercel (see `DEPLOYMENT_VERCEL.md`)
3. ⏳ Update Raspberry Pi to use production API
4. ⏳ Test end-to-end workflow

---

**Your backend is now live on Digital Ocean!** 🚀

**API URL**: `https://YOUR_DOMAIN.com` or `http://YOUR_DROPLET_IP`
