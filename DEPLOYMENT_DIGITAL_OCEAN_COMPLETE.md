# Complete Digital Ocean Deployment Guide
## Deploy Everything on One Droplet

## Overview

Deploy your entire Fridge Observer stack on a single Digital Ocean droplet:
- ✅ Backend API (FastAPI)
- ✅ Frontend (HTML/CSS/JS)
- ✅ Database (PostgreSQL or SQLite)
- ✅ Nginx (reverse proxy + static file serving)
- ✅ SSL certificates (Let's Encrypt)

**Cost**: $12-18/month for everything (vs $12/month + Vercel + Supabase separately)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              DIGITAL OCEAN DROPLET                          │
│                                                             │
│  Internet → Nginx (Port 80/443)                            │
│              ↓                                              │
│         ┌────┴────┐                                         │
│         │         │                                         │
│    Static Files   FastAPI (Port 8000)                      │
│    (Frontend)          ↓                                    │
│                   PostgreSQL/SQLite                         │
│                                                             │
│  Raspberry Pi ──WiFi──→ API                                │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- [ ] Digital Ocean account
- [ ] Domain name (optional but recommended for SSL)
- [ ] API keys (Gemini, Replicate)
- [ ] 30-45 minutes

## Step 1: Create Droplet (5 minutes)

### 1.1 Create Droplet

1. Go to [Digital Ocean](https://cloud.digitalocean.com/)
2. Click **Create** → **Droplets**
3. Choose:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic
   - **CPU**: Regular - $18/month (4 GB RAM / 2 CPU) *recommended for database*
   - Or: $12/month (2 GB RAM / 1 CPU) *works but tight on memory*
   - **Datacenter**: Closest to you
   - **Authentication**: SSH Key (recommended)
   - **Hostname**: `fridge-observer`

4. Click **Create Droplet**
5. Note the IP address: `YOUR_DROPLET_IP`

### 1.2 Initial Setup

SSH into droplet:

```bash
ssh root@YOUR_DROPLET_IP
```

Update system:

```bash
apt update && apt upgrade -y
```

Create user:

```bash
adduser fridge
usermod -aG sudo fridge
rsync --archive --chown=fridge:fridge ~/.ssh /home/fridge
su - fridge
```

## Step 2: Install All Dependencies (15 minutes)

### 2.1 Install Python

```bash
sudo apt install -y python3.11 python3.11-venv python3-pip
```

### 2.2 Install PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
```

### 2.3 Install Nginx

```bash
sudo apt install -y nginx
```

### 2.4 Install Certbot (for SSL)

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2.5 Install Git

```bash
sudo apt install -y git
```

## Step 3: Setup Database (10 minutes)

### Option A: PostgreSQL (Recommended for Production)

#### 3.1 Create Database

```bash
sudo -u postgres psql
```

In PostgreSQL shell:

```sql
CREATE DATABASE fridge_observer;
CREATE USER fridge_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE fridge_observer TO fridge_user;
\q
```

#### 3.2 Test Connection

```bash
psql -h localhost -U fridge_user -d fridge_observer
# Enter password when prompted
# Type \q to exit
```

### Option B: SQLite (Simpler, Good for Small Scale)

No setup needed! The app will create `fridge.db` automatically.

**Note**: For this guide, we'll use SQLite for simplicity. You can switch to PostgreSQL later if needed.

## Step 4: Clone and Setup Application (10 minutes)

### 4.1 Clone Repository

```bash
cd /home/fridge
git clone https://github.com/7dracoder/ClearChill.git
cd ClearChill
```

### 4.2 Create Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 4.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 Create Production .env

```bash
nano .env
```

Add:

```env
# Supabase (optional - only if you want to use Supabase instead of local DB)
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
SECRET_KEY=GENERATE_THIS_WITH_OPENSSL
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database (if using PostgreSQL)
# DATABASE_URL=postgresql://fridge_user:your_password@localhost/fridge_observer

# For SQLite (default)
# No DATABASE_URL needed - will use fridge.db
```

**Generate SECRET_KEY**:

```bash
openssl rand -hex 32
```

Copy the output and paste it as SECRET_KEY value.

Save: **Ctrl+X**, **Y**, **Enter**

### 4.5 Set Permissions

```bash
chmod 600 .env
```

### 4.6 Initialize Database

If using SQLite (default):

```bash
# Database will be created automatically on first run
python -c "from fridge_observer.db import init_db; import asyncio; asyncio.run(init_db())"
```

If using PostgreSQL:

```bash
# Update fridge_observer/db.py to use PostgreSQL connection string
# Then run migrations
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
WorkingDirectory=/home/fridge/ClearChill
Environment="PATH=/home/fridge/ClearChill/.venv/bin"
ExecStart=/home/fridge/ClearChill/.venv/bin/uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.2 Enable and Start

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

Press **Ctrl+C** to stop viewing logs.

## Step 6: Configure Nginx (15 minutes)

### 6.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/fridge-observer
```

**If you have a domain**:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Increase upload size for images
    client_max_body_size 10M;

    # Serve static files (frontend)
    location /static/ {
        alias /home/fridge/ClearChill/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # Frontend pages
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**If you DON'T have a domain** (using IP only):

```nginx
server {
    listen 80;
    server_name YOUR_DROPLET_IP;

    client_max_body_size 10M;

    location /static/ {
        alias /home/fridge/ClearChill/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6.2 Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/fridge-observer /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site
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

## Step 7: Setup SSL (Optional, 5 minutes)

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

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

Check status:

```bash
sudo ufw status
```

## Step 9: Test Everything (5 minutes)

### 9.1 Test API

```bash
curl http://YOUR_DROPLET_IP/api/health
# or with domain
curl https://yourdomain.com/api/health
```

### 9.2 Test Frontend

Open in browser:
- With domain: `https://yourdomain.com`
- Without domain: `http://YOUR_DROPLET_IP`

You should see the login page!

### 9.3 Test Full Flow

1. Create an account
2. Login
3. Add an item manually
4. Check if it appears in inventory
5. Test WebSocket (should see real-time updates)

## Step 10: Update Raspberry Pi (5 minutes)

On your Raspberry Pi, update `.env`:

```bash
nano ~/ClearChill/.env
```

Change:

```env
# With domain
API_BASE_URL=https://yourdomain.com

# Without domain
API_BASE_URL=http://YOUR_DROPLET_IP
```

Restart sensor:

```bash
sudo systemctl restart fridge-observer
```

## Database Management

### SQLite

**Backup**:

```bash
cp /home/fridge/ClearChill/fridge.db /home/fridge/backups/fridge_$(date +%Y%m%d).db
```

**View data**:

```bash
sqlite3 /home/fridge/ClearChill/fridge.db
.tables
SELECT * FROM food_items;
.quit
```

### PostgreSQL

**Backup**:

```bash
pg_dump -U fridge_user fridge_observer > backup_$(date +%Y%m%d).sql
```

**Restore**:

```bash
psql -U fridge_user fridge_observer < backup_20260418.sql
```

## Monitoring

### Check Service Status

```bash
sudo systemctl status fridge-observer
```

### View Logs

```bash
# Real-time
sudo journalctl -u fridge-observer -f

# Last 100 lines
sudo journalctl -u fridge-observer -n 100

# Today's logs
sudo journalctl -u fridge-observer --since today
```

### Check Nginx Logs

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Monitor Resources

```bash
# Install htop
sudo apt install htop

# View resources
htop

# Disk usage
df -h

# Memory usage
free -h
```

## Automated Backups

### Create Backup Script

```bash
nano ~/backup.sh
```

Add:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/fridge/backups"

mkdir -p $BACKUP_DIR

# Backup database
cp /home/fridge/ClearChill/fridge.db $BACKUP_DIR/fridge_$DATE.db

# Keep only last 7 days
find $BACKUP_DIR -name "fridge_*.db" -mtime +7 -delete

echo "Backup completed: fridge_$DATE.db"
```

Make executable:

```bash
chmod +x ~/backup.sh
```

### Schedule Daily Backups

```bash
crontab -e
```

Add:

```
0 2 * * * /home/fridge/backup.sh
```

This runs backup daily at 2 AM.

## Continuous Deployment

### Manual Update

```bash
ssh fridge@YOUR_DROPLET_IP
cd /home/fridge/ClearChill
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fridge-observer
```

### Automated with GitHub Actions

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
      - name: Deploy
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DO_HOST }}
          username: fridge
          key: ${{ secrets.DO_SSH_KEY }}
          script: |
            cd /home/fridge/ClearChill
            git pull origin main
            source .venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart fridge-observer
```

Add secrets in GitHub repo settings:
- `DO_HOST`: Your droplet IP
- `DO_SSH_KEY`: Your private SSH key

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u fridge-observer -n 50

# Test manually
cd /home/fridge/ClearChill
source .venv/bin/activate
uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8000
```

### Nginx 502 Bad Gateway

```bash
# Check if service is running
sudo systemctl status fridge-observer

# Restart both
sudo systemctl restart fridge-observer
sudo systemctl restart nginx
```

### Database Connection Issues

```bash
# Check if database file exists
ls -la /home/fridge/ClearChill/fridge.db

# Check permissions
sudo chown fridge:fridge /home/fridge/ClearChill/fridge.db
```

### Out of Memory

```bash
# Check memory
free -h

# If low, add swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Can't Access from Browser

```bash
# Check firewall
sudo ufw status

# Check if nginx is running
sudo systemctl status nginx

# Check if port 80/443 is open
sudo netstat -tulpn | grep :80
```

## Performance Optimization

### Enable Gzip Compression

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

Restart nginx:

```bash
sudo systemctl restart nginx
```

### Optimize Database

For SQLite:

```bash
sqlite3 /home/fridge/ClearChill/fridge.db "VACUUM;"
```

For PostgreSQL:

```bash
sudo -u postgres psql fridge_observer -c "VACUUM ANALYZE;"
```

## Cost Breakdown

**Digital Ocean Droplet**:
- 2 GB RAM: $12/month (tight but works)
- 4 GB RAM: $18/month (recommended)

**Domain** (optional):
- $10-15/year

**Total**: $12-18/month for everything!

**vs Split Deployment**:
- Digital Ocean: $12/month
- Vercel: Free (but limited)
- Supabase: Free (but limited) or $25/month
- Total: $12-37/month

## Advantages of All-in-One Deployment

✅ **Simpler**: Everything in one place
✅ **Cheaper**: One server instead of multiple services
✅ **Faster**: No network latency between services
✅ **More Control**: Full access to everything
✅ **Easier Debugging**: All logs in one place
✅ **No Vendor Lock-in**: Can move anywhere

## Disadvantages

❌ **Single Point of Failure**: If droplet goes down, everything is down
❌ **Manual Scaling**: Need to upgrade droplet manually
❌ **More Maintenance**: You manage everything

## When to Split Services

Consider splitting when:
- Traffic exceeds 10,000 requests/day
- Database size exceeds 10 GB
- Need geographic distribution
- Want automatic scaling
- Team prefers managed services

## Next Steps

1. ✅ Deploy everything to Digital Ocean
2. ⏳ Test from browser
3. ⏳ Update Raspberry Pi configuration
4. ⏳ Test hardware integration
5. ⏳ Setup automated backups
6. ⏳ Monitor performance

---

**Your complete stack is now running on Digital Ocean!** 🚀

**Access your app**:
- With domain: `https://yourdomain.com`
- Without domain: `http://YOUR_DROPLET_IP`

**Everything is self-contained and under your control!**
