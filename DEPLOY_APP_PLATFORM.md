# Deploy to Digital Ocean App Platform

**Easiest deployment method** - No server management, automatic scaling, built-in SSL.

## Why App Platform?

✅ **Easier** - No SSH, no server setup, just connect GitHub
✅ **Automatic** - Auto-deploys on every git push
✅ **Managed** - Digital Ocean handles everything
✅ **SSL** - Free HTTPS automatically
✅ **Scaling** - Auto-scales if needed

**Cost**: $12/month (Basic plan) - Same as droplet but fully managed!

## Prerequisites

- [ ] GitHub account with ClearChill repository
- [ ] Digital Ocean account
- [ ] Supabase project (free tier)
- [ ] API keys (Gemini, Replicate)
- [ ] 15 minutes

## Step 1: Prepare Repository (2 minutes)

Your repository is already ready! But let's verify:

### 1.1 Check Files

Make sure you have:
- ✅ `requirements.txt` - Python dependencies
- ✅ `fridge_observer/main.py` - FastAPI app
- ✅ `static/` folder - Frontend files

### 1.2 Create App Platform Config (Optional)

Create `.do/app.yaml` for better control:

```bash
mkdir -p .do
nano .do/app.yaml
```

Add:

```yaml
name: clearchill
region: nyc
services:
  - name: web
    github:
      repo: 7dracoder/ClearChill
      branch: main
      deploy_on_push: true
    
    # Build settings
    build_command: pip install -r requirements.txt
    
    # Run command
    run_command: uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8080
    
    # Environment
    envs:
      - key: PORT
        value: "8080"
      - key: HOST
        value: "0.0.0.0"
      - key: ENVIRONMENT
        value: "production"
    
    # Instance size
    instance_size_slug: basic-xxs
    instance_count: 1
    
    # Health check
    health_check:
      http_path: /api/health
    
    # Static files
    routes:
      - path: /static
        preserve_path_prefix: true

static_sites:
  - name: frontend
    github:
      repo: 7dracoder/ClearChill
      branch: main
      deploy_on_push: true
    source_dir: /static
    output_dir: /static
```

Commit:

```bash
git add .do/app.yaml
git commit -m "feat: add App Platform configuration"
git push origin main
```

## Step 2: Deploy to App Platform (10 minutes)

### 2.1 Create App

1. Go to [Digital Ocean App Platform](https://cloud.digitalocean.com/apps)
2. Click **Create App**
3. Choose **GitHub** as source
4. Authorize Digital Ocean to access your GitHub
5. Select repository: **7dracoder/ClearChill**
6. Select branch: **main**
7. Click **Next**

### 2.2 Configure Resources

Digital Ocean will auto-detect your app. Configure:

**Web Service:**
- **Name**: `clearchill-api`
- **Type**: Web Service
- **Build Command**: `pip install -r requirements.txt`
- **Run Command**: `uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8080`
- **HTTP Port**: `8080`
- **Instance Size**: Basic ($12/month)
- **Instance Count**: 1

**Static Site** (for frontend):
- **Name**: `clearchill-frontend`
- **Type**: Static Site
- **Output Directory**: `/static`

Click **Next**

### 2.3 Add Environment Variables

Click **Edit** next to Environment Variables and add:

```env
# Supabase (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# AI APIs (REQUIRED)
GEMINI_API_KEY=your_gemini_api_key
REPLICATE_API_TOKEN=your_replicate_token

# Optional
K2_API_KEY=your_k2_api_key

# Server (REQUIRED)
HOST=0.0.0.0
PORT=8080
ENVIRONMENT=production

# Security (REQUIRED)
SECRET_KEY=GENERATE_WITH_OPENSSL
ALLOWED_ORIGINS=${APP_URL}

# Email (Optional)
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

**Generate SECRET_KEY locally:**

```bash
openssl rand -hex 32
```

Copy and paste as SECRET_KEY value.

**Note**: `${APP_URL}` is automatically set by App Platform to your app's URL.

Click **Save**

### 2.4 Configure App Info

- **App Name**: `clearchill`
- **Region**: Choose closest to you (e.g., `New York`)

Click **Next**

### 2.5 Review and Deploy

- Review all settings
- Click **Create Resources**

App Platform will now:
1. Clone your repository
2. Install dependencies
3. Build your app
4. Deploy to production
5. Assign a URL

**Wait 5-10 minutes** for first deployment.

## Step 3: Get Your App URL (1 minute)

After deployment completes:

1. Go to your app dashboard
2. You'll see your app URL: `https://clearchill-xxxxx.ondigitalocean.app`
3. **Copy this URL** - you'll need it for the Raspberry Pi!

Test it:
- Open the URL in browser
- You should see the login page
- Try creating an account

## Step 4: Configure Custom Domain (Optional, 5 minutes)

### 4.1 Add Domain in App Platform

1. Go to **Settings** → **Domains**
2. Click **Add Domain**
3. Enter your domain: `yourdomain.com`
4. App Platform will show DNS records

### 4.2 Update DNS

In your domain registrar, add:

**CNAME Record:**
- **Name**: `@` (or `www`)
- **Value**: `clearchill-xxxxx.ondigitalocean.app`

Wait 5-10 minutes for DNS propagation.

### 4.3 Verify

App Platform will automatically provision SSL certificate!

## Step 5: Update Raspberry Pi Configuration (2 minutes)

On your Raspberry Pi, you need to update the `.env` file with your deployed app URL.

### What You Need:

1. **API_BASE_URL** - Your App Platform URL
2. **API_TOKEN** - JWT token from logging in

### Steps:

**On your Raspberry Pi:**

```bash
# Edit .env file
nano ~/ClearChill/.env
```

Update:

```env
# Your App Platform URL (from Step 3)
API_BASE_URL=https://clearchill-xxxxx.ondigitalocean.app

# WiFi Configuration (Princeton eduroam)
WIFI_SSID=eduroam
WIFI_USERNAME=ts5789@nyu.edu
WIFI_PASSWORD=95835576

# Hardware settings (keep as is)
LIGHT_SENSOR_PIN=17
LIGHT_THRESHOLD=0.5
CAPTURE_DELAY=2
WEBCAM_INDEX=0

# API Token (get this after logging in - see below)
API_TOKEN=your_jwt_token_here
```

Save: **Ctrl+X**, **Y**, **Enter**

### Getting API_TOKEN:

**Method 1: From Browser (Easiest)**

1. Open your app URL in browser
2. Login to your account
3. Open browser console (F12)
4. Go to **Application** → **Cookies**
5. Find cookie named `fridge_session`
6. Copy the value
7. Paste as `API_TOKEN` in Pi's `.env`

**Method 2: Using curl**

```bash
# On your Pi or computer
curl -X POST https://clearchill-xxxxx.ondigitalocean.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}'
```

Copy the token from the response.

### Restart Pi Service:

```bash
sudo systemctl restart fridge-observer
```

## Step 6: Test Everything (2 minutes)

### 6.1 Test Web App

1. Open your app URL
2. Create an account
3. Login
4. Add a test item manually
5. Check if it appears in inventory

### 6.2 Test Raspberry Pi Connection

On your Pi:

```bash
# Check if service is running
sudo systemctl status fridge-observer

# View logs
sudo journalctl -u fridge-observer -f
```

Open your fridge door - you should see:
- Door event logged
- Image captured
- Items detected
- Items added to inventory

Check your web app - new items should appear!

## Automatic Deployments

Every time you push to GitHub, App Platform automatically:
1. Pulls latest code
2. Rebuilds app
3. Deploys to production
4. Zero downtime!

```bash
# Make changes
git add .
git commit -m "feat: add new feature"
git push origin main

# App Platform deploys automatically in ~2 minutes
```

## Monitoring

### View Logs

1. Go to App Platform dashboard
2. Click on your app
3. Go to **Runtime Logs**
4. See real-time logs

### View Metrics

1. Go to **Insights** tab
2. See:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Alerts

1. Go to **Settings** → **Alerts**
2. Configure alerts for:
   - High CPU
   - High memory
   - Failed deployments
   - Downtime

## Scaling

### Manual Scaling

1. Go to **Settings** → **Resources**
2. Increase instance count (horizontal scaling)
3. Or upgrade instance size (vertical scaling)

### Auto-Scaling (Pro plan)

Upgrade to Pro plan ($25/month) for:
- Auto-scaling based on load
- More resources
- Better performance

## Cost Breakdown

**Basic Plan**: $12/month
- 512 MB RAM
- 1 vCPU
- 1 GB disk
- Perfect for your use case!

**Pro Plan**: $25/month
- 1 GB RAM
- 1 vCPU
- Auto-scaling
- Better for high traffic

**Plus Supabase**: Free tier (500MB database)

**Total**: $12/month for everything!

## Advantages vs Manual Droplet

✅ **Easier** - No SSH, no server management
✅ **Automatic** - Auto-deploys on git push
✅ **Managed** - Digital Ocean handles updates, security
✅ **SSL** - Free HTTPS automatically
✅ **Monitoring** - Built-in logs and metrics
✅ **Scaling** - Easy to scale up/down
✅ **Rollback** - Easy to rollback deployments

## Disadvantages

❌ **Less Control** - Can't SSH into server
❌ **More Expensive** - $12/month vs $6/month for smallest droplet
❌ **Limited Customization** - Can't install custom software

## Troubleshooting

### Build Failed

Check build logs:
1. Go to **Activity** tab
2. Click on failed deployment
3. View build logs
4. Fix errors in code
5. Push to GitHub

### App Crashed

Check runtime logs:
1. Go to **Runtime Logs**
2. Look for errors
3. Common issues:
   - Missing environment variables
   - Database connection failed
   - Port mismatch

### Can't Connect from Pi

1. Check API_BASE_URL is correct
2. Check API_TOKEN is valid
3. Check Pi has internet connection
4. Check firewall settings

### Slow Performance

1. Check **Insights** for resource usage
2. If high CPU/memory, upgrade instance
3. Or enable auto-scaling (Pro plan)

## Next Steps

1. ✅ Deploy to App Platform
2. ✅ Get your app URL
3. ✅ Update Raspberry Pi `.env`
4. ✅ Test hardware integration
5. ⏳ Add custom domain (optional)
6. ⏳ Setup monitoring alerts

---

**Your app is now live on Digital Ocean App Platform!** 🚀

**App URL**: `https://clearchill-xxxxx.ondigitalocean.app`

**Raspberry Pi needs**:
- `API_BASE_URL` - Your app URL
- `API_TOKEN` - JWT token from login
- WiFi credentials already in `.env`

**Everything auto-deploys on git push!** 🎉
