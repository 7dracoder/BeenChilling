# Vercel Deployment Guide - Frontend

## Overview

Deploy your Fridge Observer frontend to Vercel for fast, global CDN delivery with automatic HTTPS and continuous deployment.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION SETUP                         │
└─────────────────────────────────────────────────────────────┘

User Browser
     │
     ↓
Vercel CDN (Frontend)
     │ Static Files (HTML, CSS, JS)
     │
     ↓ API Calls
Digital Ocean (Backend)
     │ FastAPI Server
     │
     ↓
Supabase Database
```

## Prerequisites

- [ ] GitHub repository with frontend code
- [ ] Vercel account (free tier works!)
- [ ] Backend deployed to Digital Ocean
- [ ] Backend API URL

## Step 1: Prepare Frontend for Deployment (10 minutes)

### 1.1 Create vercel.json Configuration

Create `vercel.json` in project root:

```bash
nano vercel.json
```

Add:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "static/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*\\.(html|css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot))",
      "dest": "/$1"
    },
    {
      "src": "/",
      "dest": "/static/index.html"
    },
    {
      "src": "/login",
      "dest": "/static/login.html"
    },
    {
      "src": "/signup",
      "dest": "/static/login.html"
    }
  ],
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### 1.2 Update API URLs in Frontend

Update all API calls to use environment variable:

**In `static/js/config.js`** (create if doesn't exist):

```javascript
// API Configuration
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'
  : 'https://your-api.yourdomain.com'; // Your Digital Ocean backend

export { API_BASE_URL };
```

**Update all fetch calls** to use `API_BASE_URL`:

```javascript
// Before
fetch('/api/inventory')

// After
import { API_BASE_URL } from './config.js';
fetch(`${API_BASE_URL}/api/inventory`)
```

### 1.3 Update WebSocket Connection

**In `static/js/websocket.js`** (or wherever WebSocket is used):

```javascript
const WS_URL = window.location.hostname === 'localhost'
  ? 'ws://localhost:8000/ws'
  : 'wss://your-api.yourdomain.com/ws'; // Your Digital Ocean backend

const ws = new WebSocket(WS_URL);
```

### 1.4 Create .vercelignore

```bash
nano .vercelignore
```

Add:

```
.venv/
__pycache__/
*.pyc
.env
.env.local
fridge_observer/
*.db
*.log
node_modules/
.git/
```

## Step 2: Deploy to Vercel (5 minutes)

### Option A: Deploy via Vercel Dashboard (Easiest)

1. Go to [vercel.com](https://vercel.com)
2. Sign up/Login with GitHub
3. Click **Add New** → **Project**
4. Import your GitHub repository
5. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as is)
   - **Build Command**: (leave empty)
   - **Output Directory**: `static`
6. Click **Deploy**
7. Wait 1-2 minutes
8. Done! Your site is live at `https://your-project.vercel.app`

### Option B: Deploy via Vercel CLI

Install Vercel CLI:

```bash
npm install -g vercel
```

Login:

```bash
vercel login
```

Deploy:

```bash
# From project root
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? fridge-observer
# - Directory? ./
# - Override settings? No
```

Production deployment:

```bash
vercel --prod
```

## Step 3: Configure Custom Domain (Optional, 10 minutes)

### 3.1 Add Domain in Vercel

1. Go to your project in Vercel
2. Click **Settings** → **Domains**
3. Add your domain: `yourdomain.com`
4. Vercel will show DNS records to add

### 3.2 Update DNS Records

In your domain registrar:

**For Vercel:**
- **Type**: CNAME
- **Name**: `www`
- **Value**: `cname.vercel-dns.com`

**For root domain:**
- **Type**: A
- **Name**: `@`
- **Value**: `76.76.21.21`

Wait 5-10 minutes for DNS propagation.

### 3.3 Verify Domain

In Vercel, click **Verify** next to your domain.

SSL certificate will be automatically provisioned!

## Step 4: Configure Environment Variables (5 minutes)

### 4.1 Add Environment Variables in Vercel

1. Go to **Settings** → **Environment Variables**
2. Add:

```
API_BASE_URL = https://your-api.yourdomain.com
WS_URL = wss://your-api.yourdomain.com/ws
```

3. Click **Save**

### 4.2 Update Frontend to Use Environment Variables

**In `static/js/config.js`**:

```javascript
// Use environment variable if available, fallback to hardcoded
const API_BASE_URL = process.env.API_BASE_URL || 
  (window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'
    : 'https://your-api.yourdomain.com');

const WS_URL = process.env.WS_URL ||
  (window.location.hostname === 'localhost'
    ? 'ws://localhost:8000/ws'
    : 'wss://your-api.yourdomain.com/ws');

export { API_BASE_URL, WS_URL };
```

## Step 5: Update Backend CORS (5 minutes)

### 5.1 Update Digital Ocean Backend

SSH into your Digital Ocean droplet:

```bash
ssh fridge@YOUR_DROPLET_IP
```

Edit `.env`:

```bash
cd /home/fridge/fridge-observer
nano .env
```

Update CORS origins:

```env
ALLOWED_ORIGINS=https://your-project.vercel.app,https://yourdomain.com,https://www.yourdomain.com
CORS_ORIGINS=["https://your-project.vercel.app","https://yourdomain.com","https://www.yourdomain.com"]
```

Restart service:

```bash
sudo systemctl restart fridge-observer
```

### 5.2 Update FastAPI CORS Middleware

**In `fridge_observer/main.py`**, ensure CORS is configured:

```python
from fastapi.middleware.cors import CORSMiddleware
import os

# Get allowed origins from environment
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 6: Test Deployment (5 minutes)

### 6.1 Test Frontend

Open your Vercel URL: `https://your-project.vercel.app`

Check:
- ✅ Page loads
- ✅ Login works
- ✅ API calls work
- ✅ WebSocket connects
- ✅ Images load

### 6.2 Test API Connection

Open browser console (F12) and check:

```javascript
// Should show your backend URL
console.log(API_BASE_URL);

// Test API call
fetch(`${API_BASE_URL}/api/health`)
  .then(r => r.json())
  .then(d => console.log(d));
// Should log: {status: "ok"}
```

### 6.3 Test WebSocket

In browser console:

```javascript
const ws = new WebSocket(WS_URL);
ws.onopen = () => console.log('WebSocket connected!');
ws.onerror = (e) => console.error('WebSocket error:', e);
```

Should see: "WebSocket connected!"

## Step 7: Setup Continuous Deployment (Automatic!)

Vercel automatically deploys on every push to your GitHub repository!

### How it Works

1. Push code to GitHub
2. Vercel detects push
3. Builds and deploys automatically
4. Live in ~30 seconds!

### Preview Deployments

- **Main branch** → Production (`your-project.vercel.app`)
- **Other branches** → Preview URLs (`branch-name-your-project.vercel.app`)
- **Pull requests** → Preview URLs with comments

### Deployment Notifications

Enable in **Settings** → **Git** → **Deploy Hooks**:
- Slack notifications
- Discord webhooks
- Email alerts

## Step 8: Performance Optimization (10 minutes)

### 8.1 Enable Compression

Vercel automatically compresses files, but you can optimize:

**Minify JavaScript:**

```bash
# Install terser
npm install -g terser

# Minify files
terser static/js/app.js -o static/js/app.min.js -c -m
```

Update HTML to use minified version:

```html
<script src="/static/js/app.min.js"></script>
```

### 8.2 Optimize Images

```bash
# Install imagemin
npm install -g imagemin-cli imagemin-webp

# Convert to WebP
imagemin static/images/*.{jpg,png} --out-dir=static/images --plugin=webp
```

### 8.3 Add Service Worker (PWA)

Create `static/sw.js`:

```javascript
const CACHE_NAME = 'fridge-observer-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/images/logo.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
```

Register in `static/index.html`:

```html
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/sw.js');
}
</script>
```

## Monitoring & Analytics

### Vercel Analytics

1. Go to **Analytics** tab in Vercel
2. View:
   - Page views
   - Unique visitors
   - Top pages
   - Performance metrics

### Add Google Analytics (Optional)

In `static/index.html`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## Troubleshooting

### 404 Errors

Check `vercel.json` routes are correct:

```bash
vercel logs
```

### API Calls Failing

1. Check CORS settings in backend
2. Verify API_BASE_URL is correct
3. Check browser console for errors
4. Test API directly: `curl https://your-api.yourdomain.com/api/health`

### WebSocket Not Connecting

1. Verify WS_URL uses `wss://` (not `ws://`)
2. Check backend WebSocket endpoint
3. Test with: `wscat -c wss://your-api.yourdomain.com/ws`

### Slow Loading

1. Check Vercel Analytics for performance
2. Optimize images
3. Minify JavaScript/CSS
4. Enable caching

## Cost

**Vercel Free Tier includes:**
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Preview deployments
- ✅ Analytics

**Upgrade to Pro ($20/month) for:**
- More bandwidth
- Password protection
- Advanced analytics
- Priority support

## Vercel CLI Commands

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs

# List deployments
vercel ls

# Remove deployment
vercel rm <deployment-url>

# Open project in browser
vercel open
```

## GitHub Actions Integration (Optional)

Create `.github/workflows/vercel.yml`:

```yaml
name: Vercel Deployment

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

Add secrets in GitHub repository settings.

## Security Best Practices

1. ✅ Use HTTPS (automatic with Vercel)
2. ✅ Set proper CORS origins
3. ✅ Don't commit API keys
4. ✅ Use environment variables
5. ✅ Enable security headers
6. ✅ Regular dependency updates

## Next Steps

1. ✅ Deploy frontend to Vercel
2. ✅ Configure custom domain
3. ✅ Update backend CORS
4. ✅ Test end-to-end
5. ⏳ Monitor performance
6. ⏳ Add analytics

---

**Your frontend is now live on Vercel!** 🚀

**Frontend URL**: `https://your-project.vercel.app`
**Backend URL**: `https://your-api.yourdomain.com`

**Full stack deployed!** 🎉
