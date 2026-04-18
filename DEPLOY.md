# Deploy ClearChill - Free Hosting

Deploy your app completely **FREE** using Render.com. No credit card required!

## Why Render.com?

✅ **100% Free** - No credit card needed
✅ **Easy** - Deploy in 5 minutes
✅ **Auto-deploy** - Updates on every git push
✅ **Free SSL** - HTTPS automatically
✅ **750 hours/month** - More than enough for your use case

**Note**: Free tier spins down after 15 min of inactivity. First request after sleep takes ~30 seconds to wake up.

## Prerequisites

- [x] GitHub account with ClearChill repository
- [x] Supabase account (free tier)
- [x] Gemini API key (free)
- [x] Replicate API token (pay-as-you-go, ~$0.01 per image)
- [ ] 10 minutes

## Step 1: Get API Keys (5 minutes)

### 1.1 Supabase (Free)

1. Go to https://supabase.com
2. Sign up with GitHub
3. Create new project:
   - **Name**: clearchill
   - **Database Password**: (generate strong password)
   - **Region**: Closest to you
4. Wait 2 minutes for project creation
5. Go to **Settings** → **API**
6. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_KEY`
   - **service_role** key → `SUPABASE_SERVICE_KEY`

### 1.2 Google Gemini (Free)

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click **Create API Key**
4. Copy the key → `GEMINI_API_KEY`

### 1.3 Replicate (Pay-as-you-go)

1. Go to https://replicate.com
2. Sign up with GitHub
3. Go to **Account** → **API Tokens**
4. Copy token → `REPLICATE_API_TOKEN`
5. Add payment method (charges ~$0.01 per blueprint image)

### 1.4 Generate Secret Key

On your computer:

```bash
openssl rand -hex 32
```

Copy output → `SECRET_KEY`

## Step 2: Setup Supabase Database (3 minutes)

### 2.1 Run Migrations

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste from `supabase/migrations/20260418000001_initial_schema.sql`
4. Click **Run**
5. Create another query
6. Copy and paste from `supabase/migrations/20260418000002_email_otps.sql`
7. Click **Run**

Your database is now ready!

## Step 3: Deploy to Render.com (5 minutes)

### 3.1 Sign Up

1. Go to https://render.com
2. Click **Get Started**
3. Sign up with **GitHub**
4. Authorize Render to access your repositories

### 3.2 Create Web Service

1. Click **New +** → **Web Service**
2. Connect your repository: **7dracoder/ClearChill**
3. Configure:
   - **Name**: `clearchill`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn fridge_observer.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free**

4. Click **Advanced** → **Add Environment Variable**

Add these variables:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
GEMINI_API_KEY=your_gemini_api_key
REPLICATE_API_TOKEN=your_replicate_token
SECRET_KEY=your_generated_secret_key
HOST=0.0.0.0
ENVIRONMENT=production
```

5. Click **Create Web Service**

### 3.3 Wait for Deployment

Render will:
1. Clone your repository
2. Install dependencies
3. Start your app
4. Assign a URL

**Wait 3-5 minutes** for first deployment.

### 3.4 Get Your App URL

After deployment:
- Your URL: `https://clearchill.onrender.com`
- Or: `https://clearchill-xxxx.onrender.com`

**Copy this URL!** You'll need it for the Raspberry Pi.

## Step 4: Test Your App (2 minutes)

1. Open your Render URL in browser
2. You should see the login page
3. Create an account
4. Verify email (check spam folder)
5. Login
6. Add a test item manually
7. Check if it appears in inventory

**If everything works, you're done!** 🎉

## Step 5: Configure Raspberry Pi (5 minutes)

### 5.1 Get API Token

1. Open your app in browser
2. Login
3. Press **F12** → **Application** → **Cookies**
4. Find `fridge_session` cookie
5. Copy the value (starts with `eyJ...`)

### 5.2 Update Pi Configuration

On your Raspberry Pi:

```bash
cd ~/ClearChill
nano .env
```

Update:

```env
# Your Render app URL
API_BASE_URL=https://clearchill.onrender.com

# JWT token from browser
API_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Princeton eduroam WiFi
WIFI_SSID=eduroam
WIFI_USERNAME=ts5789@nyu.edu
WIFI_PASSWORD=95835576

# Hardware settings
LIGHT_SENSOR_PIN=17
LIGHT_THRESHOLD=0.5
CAPTURE_DELAY=2
WEBCAM_INDEX=0
```

Save: **Ctrl+X**, **Y**, **Enter**

### 5.3 Setup WiFi

```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Add:

```conf
network={
    ssid="eduroam"
    key_mgmt=WPA-EAP
    eap=PEAP
    identity="ts5789@nyu.edu"
    password="95835576"
    phase2="auth=MSCHAPV2"
}
```

Restart WiFi:

```bash
sudo systemctl restart wpa_supplicant
```

### 5.4 Test Connection

```bash
# Test internet
ping -c 3 google.com

# Test your app
curl https://clearchill.onrender.com/api/health
```

Should return: `{"status":"ok"}`

### 5.5 Run Sensor Script

```bash
cd ~/ClearChill
python raspberry_pi_sensor.py
```

Open fridge door → Should detect items!

## Automatic Deployments

Every time you push to GitHub:

```bash
git add .
git commit -m "update"
git push origin main
```

Render automatically:
1. Detects the push
2. Rebuilds your app
3. Deploys new version
4. Takes ~2 minutes

## Important: Free Tier Limitations

### Sleep After Inactivity

Free tier spins down after **15 minutes** of no requests.

**What this means:**
- First request after sleep: ~30 seconds to wake up
- Subsequent requests: Fast (normal speed)
- Your Pi will wake it up automatically

**Solution for Pi:**
Add a keep-alive ping in `raspberry_pi_sensor.py` (already included):

```python
# Pings API every 10 minutes to keep it awake
```

### 750 Hours/Month Limit

Free tier gives **750 hours/month** of runtime.

**Your usage:**
- 24 hours/day × 30 days = 720 hours/month
- You're within the limit! ✅

**If you exceed:**
- App stops working
- Upgrade to paid plan ($7/month)

## Monitoring

### View Logs

1. Go to Render dashboard
2. Click on your service
3. Go to **Logs** tab
4. See real-time logs

### View Metrics

1. Go to **Metrics** tab
2. See:
   - Request count
   - Response times
   - Memory usage
   - CPU usage

### Alerts

Render will email you if:
- Deployment fails
- App crashes
- Approaching hour limit

## Troubleshooting

### App Won't Start

Check logs in Render dashboard:
- Missing environment variables?
- Python version mismatch?
- Dependency installation failed?

### Can't Connect from Pi

```bash
# Check if app is awake
curl https://clearchill.onrender.com/api/health

# If slow, app is waking up (wait 30 seconds)

# Check API_BASE_URL
cat .env | grep API_BASE_URL

# Check API_TOKEN is valid
cat .env | grep API_TOKEN
```

### App is Slow

Free tier sleeps after 15 min inactivity.

**Solutions:**
1. Wait 30 seconds for first request
2. Pi will keep it awake with regular pings
3. Or upgrade to paid plan ($7/month) for always-on

### Database Errors

Check Supabase:
1. Go to Supabase dashboard
2. Check if migrations ran successfully
3. Go to **Table Editor** → Should see tables
4. Check **Logs** for errors

## Upgrading to Paid (Optional)

If you need always-on performance:

1. Go to Render dashboard
2. Click on your service
3. Go to **Settings** → **Plan**
4. Upgrade to **Starter** ($7/month)

**Benefits:**
- Always on (no sleep)
- Faster performance
- More resources

## Cost Summary

**Free Tier:**
- Render: **$0/month** (750 hours)
- Supabase: **$0/month** (500MB database)
- Gemini: **$0/month** (free tier)
- Replicate: **~$1-2/month** (pay per use)

**Total: ~$1-2/month** (just for image generation)

**Paid Tier (if needed):**
- Render: **$7/month** (always on)
- Everything else: Same as above

**Total: ~$8-9/month**

## Next Steps

1. ✅ Deploy to Render.com
2. ✅ Get your app URL
3. ✅ Configure Raspberry Pi
4. ✅ Test hardware integration
5. ⏳ Monitor usage
6. ⏳ Upgrade if needed

---

**Your app is now live for FREE!** 🎉

**App URL**: `https://clearchill.onrender.com`

**Raspberry Pi**: Configured with WiFi and API credentials

**Everything works wirelessly over Princeton's eduroam!** 📡

## Support

- **Render Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Issues**: Open an issue on GitHub

---

**Enjoy your smart fridge!** 🚀
