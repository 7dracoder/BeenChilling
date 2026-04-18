# Complete Deployment Guide - Digital Ocean + Vercel

## Overview

This guide walks you through deploying your Fridge Observer system to production with:
- **Backend**: Digital Ocean (FastAPI server)
- **Frontend**: Vercel (Static files)
- **Database**: Supabase (PostgreSQL)
- **Hardware**: Raspberry Pi (connects to production API)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────┘

User Browser
     │
     ↓
Vercel CDN (Frontend)
     │ https://fridge-observer.vercel.app
     │
     ↓ API Calls
Digital Ocean (Backend)
     │ https://api.yourdomain.com
     │
     ├─ FastAPI Server (Port 8000)
     ├─ Nginx (Reverse Proxy)
     ├─ SSL (Let's Encrypt)
     └─ Systemd (Auto-restart)
     │
     ↓
Supabase (Database)
     │ PostgreSQL + Auth
     │
     ↓
External APIs
     ├─ Gemini Vision (Food detection)
     ├─ Replicate (Blueprint generation)
     └─ K2-Think (AI reasoning)

Raspberry Pi (Hardware)
     │ WiFi Connection
     │
     ↓ HTTPS
Digital Ocean API
```

## Prerequisites Checklist

### Accounts
- [ ] Digital Ocean account ($12/month)
- [ ] Vercel account (Free tier)
- [ ] GitHub account (Free)
- [ ] Domain name (Optional, $10-15/year)

### API Keys
- [ ] Supabase URL and keys
- [ ] Gemini API key
- [ ] Replicate API token
- [ ] K2-Think API key (optional)

### Local Setup
- [ ] Git installed
- [ ] Code committed to GitHub
- [ ] `.env.example` created
- [ ] `requirements.txt` updated
- [ ] `vercel.json` configured

## Deployment Timeline

| Step | Task | Time | Difficulty |
|------|------|------|------------|
| 1 | Prepare Git Repository | 15 min | Easy |
| 2 | Deploy Backend (Digital Ocean) | 45 min | Medium |
| 3 | Deploy Frontend (Vercel) | 15 min | Easy |
| 4 | Configure DNS & SSL | 15 min | Easy |
| 5 | Update Raspberry Pi | 10 min | Easy |
| 6 | Test End-to-End | 10 min | Easy |

**Total Time: ~2 hours**

## Step-by-Step Deployment

### Phase 1: Prepare Repository (15 minutes)

#### 1.1 Create Git Repository

```bash
# Initialize Git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Fridge Observer with hardware integration"

# Create GitHub repository (via web interface)
# Then add remote and push
git remote add origin https://github.com/YOUR_USERNAME/fridge-observer.git
git branch -M main
git push -u origin main
```

**See**: `GIT_SETUP.md` for detailed instructions

#### 1.2 Verify Files

Ensure these files exist:
- ✅ `.gitignore`
- ✅ `.env.example`
- ✅ `requirements.txt`
- ✅ `vercel.json`
- ✅ `README.md`

### Phase 2: Deploy Backend to Digital Ocean (45 minutes)

#### 2.1 Create Droplet

1. Log in to Digital Ocean
2. Create Droplet:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic, 2GB RAM ($12/month)
   - **Datacenter**: Closest to you
   - **Authentication**: SSH Key
   - **Hostname**: `fridge-observer-api`

3. Note the IP address: `164.90.xxx.xxx`

#### 2.2 Initial Server Setup

```bash
# SSH into droplet
ssh root@YOUR_DROPLET_IP

# Update system
apt update && apt upgrade -y

# Create user
adduser fridge
usermod -aG sudo fridge

# Setup SSH for new user
rsync --archive --chown=fridge:fridge ~/.ssh /home/fridge

# Switch to new user
su - fridge
```

#### 2.3 Install Dependencies

```bash
# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Nginx
sudo apt install -y nginx

# Install Certbot (for SSL)
sudo apt install -y certbot python3-certbot-nginx

# Install Git
sudo apt install -y git
```

#### 2.4 Clone and Setup Project

```bash
# Clone repository
cd /home/fridge
git clone https://github.com/YOUR_USERNAME/fridge-observer.git
cd fridge-observer

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.5 Configure Environment

```bash
# Create .env file
nano .env
```

Add your production environment variables:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
GEMINI_API_KEY=your_gemini_api_key
K2_API_KEY=your_k2_api_key
REPLICATE_API_TOKEN=your_replicate_token
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://yourdomain.com
CORS_ORIGINS=["https://your-frontend.vercel.app","https://yourdomain.com"]
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
```

Save and set permissions:

```bash
chmod 600 .env
```

#### 2.6 Create Systemd Service

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

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fridge-observer
sudo systemctl start fridge-observer
sudo systemctl status fridge-observer
```

#### 2.7 Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/fridge-observer
```

Add:

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN.com www.YOUR_DOMAIN.com;
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
        proxy_read_timeout 86400;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/fridge-observer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 2.8 Setup SSL (if you have a domain)

```bash
# Point domain to droplet IP first (in your domain registrar)
# Wait 5-10 minutes for DNS propagation

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

#### 2.9 Configure Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

#### 2.10 Test Backend

```bash
# Test API
curl http://YOUR_DROPLET_IP/api/health
# or
curl https://yourdomain.com/api/health

# Should return: {"status":"ok"}
```

**See**: `DEPLOYMENT_DIGITAL_OCEAN.md` for detailed instructions

### Phase 3: Deploy Frontend to Vercel (15 minutes)

#### 3.1 Prepare Frontend

Ensure `vercel.json` exists in project root (already created).

#### 3.2 Deploy to Vercel

**Option A: Via Vercel Dashboard**

1. Go to [vercel.com](https://vercel.com)
2. Sign up/Login with GitHub
3. Click **Add New** → **Project**
4. Import your GitHub repository
5. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: (leave empty)
   - **Output Directory**: `static`
6. Add Environment Variables:
   - `API_BASE_URL` = `https://yourdomain.com` (or `http://YOUR_DROPLET_IP`)
   - `WS_URL` = `wss://yourdomain.com/ws` (or `ws://YOUR_DROPLET_IP/ws`)
7. Click **Deploy**
8. Wait 1-2 minutes
9. Your site is live at `https://your-project.vercel.app`

**Option B: Via Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Production deployment
vercel --prod
```

#### 3.3 Update Frontend API URLs

Create `static/js/config.js`:

```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'
  : 'https://yourdomain.com'; // Your Digital Ocean backend

const WS_URL = window.location.hostname === 'localhost'
  ? 'ws://localhost:8000/ws'
  : 'wss://yourdomain.com/ws';

export { API_BASE_URL, WS_URL };
```

Update all fetch calls to use `API_BASE_URL`.

**See**: `DEPLOYMENT_VERCEL.md` for detailed instructions

### Phase 4: Configure DNS & SSL (15 minutes)

#### 4.1 Point Domain to Services

**For Backend (Digital Ocean):**
- **Type**: A Record
- **Name**: `api` (or `@` for root)
- **Value**: `YOUR_DROPLET_IP`

**For Frontend (Vercel):**
- **Type**: CNAME
- **Name**: `www`
- **Value**: `cname.vercel-dns.com`

- **Type**: A Record
- **Name**: `@`
- **Value**: `76.76.21.21`

#### 4.2 Verify SSL

Both Digital Ocean (via Certbot) and Vercel automatically provision SSL certificates.

Test:
- Backend: `https://api.yourdomain.com/api/health`
- Frontend: `https://yourdomain.com`

### Phase 5: Update Raspberry Pi (10 minutes)

#### 5.1 Update Pi Configuration

SSH into Raspberry Pi:

```bash
ssh pi@raspberrypi.local
```

Update `.env`:

```bash
cd ~/fridge-observer
nano .env
```

Change:

```env
API_BASE_URL=https://api.yourdomain.com
# or
API_BASE_URL=http://YOUR_DROPLET_IP
```

#### 5.2 Restart Sensor

```bash
sudo systemctl restart fridge-observer
```

#### 5.3 Test Connection

```bash
# Check logs
sudo journalctl -u fridge-observer -f

# Open fridge door and verify it connects to production API
```

### Phase 6: Test End-to-End (10 minutes)

#### 6.1 Test Frontend

1. Open `https://yourdomain.com` (or Vercel URL)
2. Sign up / Log in
3. Navigate to Inventory page
4. Verify page loads

#### 6.2 Test API Connection

Open browser console (F12):

```javascript
// Test API
fetch('https://api.yourdomain.com/api/health')
  .then(r => r.json())
  .then(d => console.log(d));
// Should log: {status: "ok"}
```

#### 6.3 Test WebSocket

```javascript
const ws = new WebSocket('wss://api.yourdomain.com/ws');
ws.onopen = () => console.log('Connected!');
ws.onerror = (e) => console.error('Error:', e);
```

#### 6.4 Test Hardware Integration

1. Open fridge door on Raspberry Pi
2. Check Pi logs: `sudo journalctl -u fridge-observer -f`
3. Verify image uploaded
4. Check web app for new items
5. Confirm real-time update

## Post-Deployment Checklist

### Security
- [ ] SSL certificates active (HTTPS)
- [ ] Firewall configured (UFW)
- [ ] Strong SECRET_KEY set
- [ ] CORS origins restricted
- [ ] `.env` file permissions set (600)
- [ ] SSH key authentication only

### Monitoring
- [ ] Backend logs: `sudo journalctl -u fridge-observer -f`
- [ ] Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- [ ] Vercel Analytics enabled
- [ ] Error tracking setup (optional: Sentry)

### Backup
- [ ] Database backup strategy
- [ ] Code in Git repository
- [ ] Environment variables documented
- [ ] SSL certificates auto-renew

### Performance
- [ ] Gzip compression enabled
- [ ] Static file caching
- [ ] CDN active (Vercel)
- [ ] Image optimization

## Continuous Deployment

### Automatic Deployment

**Backend (Digital Ocean):**
- Push to `main` branch
- GitHub Actions deploys automatically
- See `.github/workflows/deploy.yml`

**Frontend (Vercel):**
- Push to any branch
- Vercel deploys automatically
- `main` → Production
- Other branches → Preview URLs

### Manual Deployment

**Backend:**
```bash
ssh fridge@YOUR_DROPLET_IP
cd /home/fridge/fridge-observer
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fridge-observer
```

**Frontend:**
```bash
vercel --prod
```

## Monitoring & Maintenance

### Daily
- Check error logs
- Monitor API response times
- Verify hardware connection

### Weekly
- Review system logs
- Check disk space
- Update dependencies (if needed)

### Monthly
- Security updates: `sudo apt update && sudo apt upgrade`
- SSL certificate renewal (automatic)
- Database backup verification
- Performance optimization

## Troubleshooting

### Backend Issues

**Service won't start:**
```bash
sudo systemctl status fridge-observer
sudo journalctl -u fridge-observer -n 50
```

**502 Bad Gateway:**
```bash
sudo systemctl restart fridge-observer
sudo systemctl restart nginx
```

### Frontend Issues

**API calls failing:**
- Check CORS settings in backend
- Verify API_BASE_URL is correct
- Check browser console for errors

**WebSocket not connecting:**
- Verify WS_URL uses `wss://` (not `ws://`)
- Check Nginx WebSocket configuration
- Test with: `wscat -c wss://api.yourdomain.com/ws`

### Hardware Issues

**Pi can't connect:**
- Verify API_BASE_URL in Pi's `.env`
- Check firewall allows connections
- Test: `curl https://api.yourdomain.com/api/health`

## Cost Summary

| Service | Plan | Cost |
|---------|------|------|
| Digital Ocean | 2GB Droplet | $12/month |
| Vercel | Free Tier | $0/month |
| Domain | Annual | $10-15/year |
| Supabase | Free Tier | $0/month |
| **Total** | | **~$13/month** |

## Success Criteria

✅ Backend API accessible via HTTPS
✅ Frontend loads on Vercel
✅ User can log in
✅ API calls work from frontend
✅ WebSocket connects
✅ Raspberry Pi connects to production API
✅ Items detected and added to inventory
✅ Real-time updates work
✅ SSL certificates active
✅ Auto-deployment configured

## Next Steps

1. ✅ Deploy to production
2. ⏳ Monitor for 24 hours
3. ⏳ Fine-tune performance
4. ⏳ Add monitoring/alerts
5. ⏳ Setup backup strategy
6. ⏳ Document any custom configurations

---

**Congratulations! Your Fridge Observer is now live in production!** 🎉

**Frontend**: `https://yourdomain.com`
**Backend**: `https://api.yourdomain.com`
**Status**: Production Ready ✅
