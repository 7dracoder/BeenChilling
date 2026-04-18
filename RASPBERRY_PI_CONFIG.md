# Raspberry Pi Configuration After Deployment

Quick reference for configuring your Raspberry Pi to connect to the deployed app.

## What You Need

After deploying to Digital Ocean App Platform, you need **2 things** for your Raspberry Pi:

1. **API_BASE_URL** - Your deployed app URL
2. **API_TOKEN** - JWT authentication token

## Step 1: Get Your App URL

From Digital Ocean App Platform dashboard:
- Your URL will be: `https://clearchill-xxxxx.ondigitalocean.app`
- Or your custom domain: `https://yourdomain.com`

**Copy this URL!**

## Step 2: Get Your API Token

### Method 1: From Browser (Easiest)

1. Open your app URL in browser
2. Create an account / Login
3. Press **F12** to open Developer Tools
4. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
5. Click **Cookies** → Your domain
6. Find cookie named `fridge_session`
7. Copy the **Value** (long string starting with `eyJ...`)

**This is your API_TOKEN!**

### Method 2: Using curl

```bash
curl -X POST https://your-app-url.ondigitalocean.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "yourpassword"
  }' \
  -c cookies.txt

# Token will be in cookies.txt
cat cookies.txt | grep fridge_session
```

## Step 3: Configure Raspberry Pi

### 3.1 SSH into Your Pi

```bash
ssh pi@YOUR_PI_IP
# or if you're on the Pi directly, skip this
```

### 3.2 Edit .env File

```bash
cd ~/ClearChill
nano .env
```

### 3.3 Update Configuration

```env
# ============================================
# DEPLOYMENT CONFIGURATION
# ============================================

# Your deployed app URL (from Step 1)
API_BASE_URL=https://clearchill-xxxxx.ondigitalocean.app

# Your JWT token (from Step 2)
API_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

# ============================================
# WIFI CONFIGURATION (Princeton eduroam)
# ============================================

WIFI_SSID=eduroam
WIFI_USERNAME=ts5789@nyu.edu
WIFI_PASSWORD=95835576

# ============================================
# HARDWARE CONFIGURATION
# ============================================

# GPIO pin for photoresistor (door sensor)
LIGHT_SENSOR_PIN=17

# Light threshold for door detection (0.0 - 1.0)
# Higher = brighter light needed to trigger
LIGHT_THRESHOLD=0.5

# Seconds to wait after door opens before capturing
CAPTURE_DELAY=2

# Webcam device index (usually 0 for first camera)
WEBCAM_INDEX=0
```

**Save**: Press **Ctrl+X**, then **Y**, then **Enter**

### 3.4 Set Permissions

```bash
chmod 600 .env
```

## Step 4: Setup WiFi (Princeton eduroam)

### 4.1 Configure wpa_supplicant

```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Add:

```conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid="eduroam"
    key_mgmt=WPA-EAP
    eap=PEAP
    identity="ts5789@nyu.edu"
    password="95835576"
    phase2="auth=MSCHAPV2"
}
```

**Save**: **Ctrl+X**, **Y**, **Enter**

### 4.2 Restart WiFi

```bash
sudo systemctl restart wpa_supplicant
sudo systemctl restart networking
```

### 4.3 Verify Connection

```bash
# Check WiFi status
iwconfig

# Check if connected to eduroam
iwgetid

# Test internet
ping -c 3 google.com

# Test your app
curl https://your-app-url.ondigitalocean.app/api/health
```

Should return: `{"status":"ok"}`

## Step 5: Install and Run Sensor Script

### 5.1 Install Dependencies

```bash
cd ~/ClearChill
source .venv/bin/activate
pip install -r requirements.txt
```

### 5.2 Test Manually

```bash
python raspberry_pi_sensor.py
```

You should see:
```
========================================
Fridge Observer - Hardware Monitor
========================================
API: https://your-app-url.ondigitalocean.app
Light sensor: GPIO 17
Threshold: 0.5
Webcam: Index 0
========================================
Monitoring started... (Press Ctrl+C to stop)
```

Open your fridge door - you should see:
```
🚪 Door OPENED (light: 0.85)
✓ Door event sent: door_opened
📸 Capturing image...
✓ Image uploaded successfully
  Total detected: 3 items
  ✓ Auto-added (2):
    - Apple (expires in 7 days)
    - Banana (expires in 5 days)
  ⏳ Needs expiry input (1):
    - Milk (Google Home will ask)
```

Press **Ctrl+C** to stop.

### 5.3 Setup as Service

Create systemd service:

```bash
sudo nano /etc/systemd/system/fridge-observer.service
```

Add:

```ini
[Unit]
Description=Fridge Observer Hardware Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ClearChill
Environment="PATH=/home/pi/ClearChill/.venv/bin"
ExecStart=/home/pi/ClearChill/.venv/bin/python /home/pi/ClearChill/raspberry_pi_sensor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save**: **Ctrl+X**, **Y**, **Enter**

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fridge-observer
sudo systemctl start fridge-observer
```

Check status:

```bash
sudo systemctl status fridge-observer
```

Should show: **Active: active (running)**

View logs:

```bash
sudo journalctl -u fridge-observer -f
```

## Step 6: Test End-to-End

### 6.1 Open Fridge Door

1. Open your fridge door
2. Wait 2 seconds
3. Close door

### 6.2 Check Pi Logs

```bash
sudo journalctl -u fridge-observer -n 50
```

Should show:
- Door opened event
- Image captured
- Items detected
- Items added

### 6.3 Check Web App

1. Open your app URL in browser
2. Login
3. Go to Inventory
4. You should see the newly detected items!

## Troubleshooting

### Pi Can't Connect to WiFi

```bash
# Check WiFi status
sudo systemctl status wpa_supplicant

# Check network interfaces
ip addr show

# Restart WiFi
sudo systemctl restart wpa_supplicant
sudo systemctl restart networking

# Check logs
sudo journalctl -u wpa_supplicant -n 50
```

### Pi Can't Reach API

```bash
# Test internet
ping -c 3 google.com

# Test API
curl https://your-app-url.ondigitalocean.app/api/health

# Check if API_BASE_URL is correct
cat .env | grep API_BASE_URL

# Check if API_TOKEN is valid (should be long string)
cat .env | grep API_TOKEN
```

### Camera Not Working

```bash
# List cameras
ls -l /dev/video*

# Test camera
raspistill -o test.jpg

# Or with USB camera
fswebcam test.jpg

# Check WEBCAM_INDEX in .env
cat .env | grep WEBCAM_INDEX
```

### Door Sensor Not Working

```bash
# Test GPIO
python3 << EOF
from gpiozero import LightSensor
sensor = LightSensor(17)
print(f"Light level: {sensor.value}")
EOF

# Adjust LIGHT_THRESHOLD if needed
nano .env
# Change LIGHT_THRESHOLD (0.0 = dark, 1.0 = bright)
```

### Service Won't Start

```bash
# Check logs
sudo journalctl -u fridge-observer -n 50

# Test manually
cd ~/ClearChill
source .venv/bin/activate
python raspberry_pi_sensor.py

# Check permissions
ls -la .env
chmod 600 .env
```

## Quick Reference

### View Logs

```bash
sudo journalctl -u fridge-observer -f
```

### Restart Service

```bash
sudo systemctl restart fridge-observer
```

### Stop Service

```bash
sudo systemctl stop fridge-observer
```

### Check Status

```bash
sudo systemctl status fridge-observer
```

### Update Code

```bash
cd ~/ClearChill
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fridge-observer
```

## Summary

**What Pi Needs:**
1. ✅ API_BASE_URL - Your deployed app URL
2. ✅ API_TOKEN - JWT token from login
3. ✅ WiFi credentials - eduroam with your NYU email
4. ✅ Hardware connected - Camera + photoresistor

**WiFi Details:**
- **SSID**: eduroam
- **Username**: ts5789@nyu.edu
- **Password**: 95835576
- **Type**: WPA-EAP (PEAP/MSCHAPV2)

**After Configuration:**
- Pi connects to eduroam WiFi
- Pi monitors fridge door
- When door opens, captures image
- Sends to your deployed app
- App detects food items
- Updates inventory in real-time

**Everything works wirelessly over Princeton's eduroam network!** 📡

---

**Your Raspberry Pi is now connected to your deployed app!** 🎉
