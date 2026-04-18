# Deployment Checklist - Do This Now!

Follow these steps **exactly** to deploy your app. Takes 15 minutes total.

## Part 1: Supabase Setup (5 minutes)

### Step 1.1: Create Supabase Project

1. Go to: https://supabase.com
2. Click **Start your project**
3. Sign in with **GitHub**
4. Click **New Project**
5. Fill in:
   - **Name**: `clearchill`
   - **Database Password**: Click "Generate a password" (SAVE THIS!)
   - **Region**: `East US (North Virginia)` (closest to you)
   - **Pricing Plan**: Free
6. Click **Create new project**
7. Wait 2 minutes for setup

### Step 1.2: Get API Keys

1. In Supabase dashboard, click **Settings** (gear icon)
2. Click **API**
3. Copy these values (you'll need them):
   ```
   Project URL: https://xxxxx.supabase.co
   anon public: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   service_role: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### Step 1.3: Run Database Migrations

1. In Supabase dashboard, click **SQL Editor** (left sidebar)
2. Click **New Query**
3. Open `supabase/migrations/20260418000001_initial_schema.sql` in your code
4. Copy ALL the SQL code
5. Paste into Supabase SQL Editor
6. Click **Run** (bottom right)
7. Should see: "Success. No rows returned"

8. Click **New Query** again
9. Open `supabase/migrations/20260418000002_email_otps.sql`
10. Copy ALL the SQL code
11. Paste into Supabase SQL Editor
12. Click **Run**
13. Should see: "Success. No rows returned"

14. Click **Table Editor** (left sidebar)
15. You should see tables: `food_items`, `recipes`, `settings`, `email_otps`, `profiles`

✅ **Supabase is ready!**

---

## Part 2: Get API Keys (3 minutes)

### Step 2.1: Google Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click **Create API Key**
4. Click **Create API key in new project**
5. Copy the key (starts with `AIza...`)
6. Save as: `GEMINI_API_KEY`

### Step 2.2: Replicate API Token

1. Go to: https://replicate.com
2. Click **Sign in** → Sign in with **GitHub**
3. Click your profile (top right) → **Account**
4. Click **API Tokens** (left sidebar)
5. Copy the token (starts with `r8_...`)
6. Save as: `REPLICATE_API_TOKEN`

### Step 2.3: Generate Secret Key

On your computer, run:

```bash
openssl rand -hex 32
```

Copy the output (64 characters)
Save as: `SECRET_KEY`

✅ **All API keys ready!**

---

## Part 3: Deploy to Render.com (7 minutes)

### Step 3.1: Sign Up

1. Go to: https://render.com
2. Click **Get Started for Free**
3. Click **GitHub** (sign in with GitHub)
4. Authorize Render to access your repositories

### Step 3.2: Create Web Service

1. Click **New +** (top right)
2. Click **Web Service**
3. Find and click **7dracoder/ClearChill**
4. Click **Connect**

### Step 3.3: Configure Service

Fill in these settings:

**Basic Settings:**
- **Name**: `clearchill` (or any name you want)
- **Region**: `Oregon (US West)` (free tier available)
- **Branch**: `main`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn fridge_observer.main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select: **Free** ($0/month)

### Step 3.4: Add Environment Variables

Scroll down to **Environment Variables**

Click **Add Environment Variable** for each:

```env
SUPABASE_URL
Value: https://xxxxx.supabase.co (from Step 1.2)

SUPABASE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (anon public from Step 1.2)

SUPABASE_SERVICE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (service_role from Step 1.2)

GEMINI_API_KEY
Value: AIza... (from Step 2.1)

REPLICATE_API_TOKEN
Value: r8_... (from Step 2.2)

SECRET_KEY
Value: (64 character string from Step 2.3)

HOST
Value: 0.0.0.0

ENVIRONMENT
Value: production
```

### Step 3.5: Deploy!

1. Click **Create Web Service** (bottom)
2. Render will start deploying
3. Watch the logs (you'll see):
   ```
   ==> Cloning from https://github.com/7dracoder/ClearChill...
   ==> Installing dependencies...
   ==> Starting service...
   ==> Your service is live 🎉
   ```
4. Wait 3-5 minutes for first deployment

### Step 3.6: Get Your App URL

1. At the top of the page, you'll see your URL:
   ```
   https://clearchill.onrender.com
   ```
   or
   ```
   https://clearchill-xxxx.onrender.com
   ```

2. **COPY THIS URL!** You need it for the Raspberry Pi

3. Click the URL to test
4. You should see the login page!

✅ **App is deployed!**

---

## Part 4: Test Your Deployment (2 minutes)

### Step 4.1: Create Account

1. Open your Render URL in browser
2. Click **Sign Up**
3. Enter:
   - Email: your email
   - Name: your name
   - Password: strong password
4. Click **Sign Up**
5. Check your email for verification code
6. Enter the 6-digit code
7. Click **Verify**

### Step 4.2: Login

1. Enter your email and password
2. Click **Login**
3. You should see the dashboard!

### Step 4.3: Test Adding Item

1. Click **Inventory** (left sidebar)
2. Click **Add Item** (top right)
3. Add a test item:
   - Name: Test Apple
   - Category: Fruits
   - Quantity: 1
   - Expiry: Tomorrow's date
4. Click **Add**
5. Item should appear in the list!

✅ **Deployment is working!**

---

## Part 5: Get API Token for Raspberry Pi (2 minutes)

### Step 5.1: Get Token from Browser

1. In your deployed app (logged in)
2. Press **F12** (opens Developer Tools)
3. Click **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Click **Cookies** → Your domain
5. Find cookie named `fridge_session`
6. Click on it
7. Copy the **Value** (long string starting with `eyJ...`)

**This is your API_TOKEN!**

Example:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

✅ **Token obtained!**

---

## Part 6: Configure Raspberry Pi (5 minutes)

### Step 6.1: Update .env File

On your Raspberry Pi:

```bash
cd ~/ClearChill
nano .env
```

Update with your values:

```env
# Your deployed app URL (from Part 3, Step 3.6)
API_BASE_URL=https://clearchill.onrender.com

# Your API token (from Part 5)
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

### Step 6.2: Setup WiFi

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

Save and restart WiFi:

```bash
sudo systemctl restart wpa_supplicant
```

### Step 6.3: Test Connection

```bash
# Test internet
ping -c 3 google.com

# Test your app
curl https://clearchill.onrender.com/api/health
```

Should return: `{"status":"ok"}`

### Step 6.4: Run Sensor Script

```bash
cd ~/ClearChill
python raspberry_pi_sensor.py
```

You should see:
```
========================================
Fridge Observer - Hardware Monitor
========================================
API: https://clearchill.onrender.com
Monitoring started...
```

**Open your fridge door** → Should detect and send image!

✅ **Raspberry Pi is connected!**

---

## Summary - What You Deployed

✅ **Supabase**: Database + Auth (FREE)
✅ **Render.com**: Backend + Frontend (FREE)
✅ **Gemini AI**: Food detection (FREE)
✅ **Replicate**: Image generation (~$1-2/month)

**Total Cost**: ~$1-2/month

**Your URLs**:
- **Web App**: https://clearchill.onrender.com
- **Supabase**: https://xxxxx.supabase.co

**Raspberry Pi**:
- Connected to Princeton eduroam WiFi
- Sends images to your deployed app
- App detects food and updates inventory

---

## Troubleshooting

### Render Deployment Failed

1. Go to Render dashboard
2. Click on your service
3. Click **Logs** tab
4. Look for errors
5. Common issues:
   - Missing environment variable
   - Wrong Python version
   - Dependency installation failed

### Can't Login to App

1. Check email for verification code
2. Check spam folder
3. Try resending code
4. Check Supabase logs

### Pi Can't Connect

1. Check WiFi: `iwconfig`
2. Check API_BASE_URL is correct
3. Check API_TOKEN is valid
4. Test: `curl https://your-app.onrender.com/api/health`

---

## Next Steps

1. ✅ Deploy to Supabase
2. ✅ Deploy to Render.com
3. ✅ Configure Raspberry Pi
4. ⏳ Test by opening fridge door
5. ⏳ Monitor usage and costs

**You're done! Your smart fridge is live!** 🎉
