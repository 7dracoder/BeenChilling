# Google Home Voice Integration Setup Guide

Complete guide to set up automatic voice notifications when items are detected in your fridge.

---

## 🎯 Overview

When you close the fridge door:
1. **Raspberry Pi** captures images and detects items using YOLOv8
2. **Your PC** receives detection results and stores pending items
3. **Google Home** automatically announces: *"I detected 3 new items in your fridge"*
4. **You respond**: *"Hey Google, what are the pending items?"*
5. **Google Home asks**: *"How many Milk?"* → You answer → *"Expiry date?"* → You answer
6. **Items are added** to your inventory automatically

---

## 📋 Prerequisites

### Hardware
- ✅ Raspberry Pi 4 (2GB+ RAM)
- ✅ Logitech Webcam (USB)
- ✅ Light sensor (for door detection)
- ✅ Google Home device
- ✅ Your PC (running FastAPI backend)

### Software
- ✅ Python 3.9+ on Raspberry Pi
- ✅ Python 3.9+ on your PC
- ✅ Supabase account (already set up)
- ✅ IFTTT account (free)
- ✅ Google Cloud account (free tier)

### Network
- ✅ All devices on same WiFi network
- ✅ Internet connection (for IFTTT and Supabase)

---

## 🚀 Part 1: IFTTT Setup (5 minutes)

### Step 1: Create IFTTT Account
1. Go to https://ifttt.com
2. Sign up for free account
3. Verify your email

### Step 2: Connect Google Assistant
1. Go to https://ifttt.com/google_assistant
2. Click **Connect**
3. Sign in with your Google account (same as Google Home)
4. Grant permissions

### Step 3: Create Webhook Applet

#### Create "Fridge Items Detected" Applet
1. Go to https://ifttt.com/create
2. Click **If This**
3. Search for **Webhooks**
4. Choose **Receive a web request**
5. Event Name: `fridge_items_detected`
6. Click **Create trigger**

7. Click **Then That**
8. Search for **Google Assistant**
9. Choose **Say a phrase with a text ingredient**
10. Configure:
    - **What do you want to say?**: `I detected {{Value1}} new items in your fridge. Say "what are the pending items" to add them.`
    - **Language**: English
11. Click **Create action**
12. Click **Continue** → **Finish**

#### Create "Item Added" Confirmation Applet
1. Create another applet: https://ifttt.com/create
2. **If This**: Webhooks → Event: `item_added_to_fridge`
3. **Then That**: Google Assistant → Say: `{{Value1}} has been added to your fridge`

### Step 4: Get Your Webhook Key
1. Go to https://ifttt.com/maker_webhooks
2. Click **Documentation**
3. Copy your key (looks like: `dA1B2c3D4e5F6g7H8i9J0`)
4. Save it - you'll need it later

### Step 5: Test IFTTT
```bash
# Replace YOUR_KEY with your actual key
curl -X POST https://maker.ifttt.com/trigger/fridge_items_detected/with/key/YOUR_KEY \
  -H "Content-Type: application/json" \
  -d '{"value1": "3"}'
```

**Your Google Home should say**: *"I detected 3 new items in your fridge..."*

✅ If it works, continue to Part 2!

---

## 🔧 Part 2: Google Actions Setup (15 minutes)

### Step 1: Create Google Cloud Project
1. Go to https://console.cloud.google.com
2. Create new project: **Fridge Observer**
3. Note your Project ID

### Step 2: Enable APIs
1. Go to **APIs & Services** → **Library**
2. Enable these APIs:
   - **Actions API**
   - **Google Assistant API**
   - **Cloud Functions API**

### Step 3: Create Actions Project
1. Go to https://console.actions.google.com
2. Click **New project**
3. Select your Google Cloud project
4. Project name: **Fridge Observer**
5. Language: **English**
6. Click **Create project**

### Step 4: Configure Actions

#### Create "Pending Items" Intent
1. Go to **Develop** → **Invocations**
2. Display name: `Fridge Observer`
3. Invocation: `fridge observer` or `my fridge`

4. Go to **Develop** → **Actions**
5. Click **Add your first action**
6. Choose **Custom intent**

7. Create intent: `get_pending_items`
   - **Training phrases**:
     - "what are the pending items"
     - "what's pending in my fridge"
     - "show me pending items"
     - "what did I add"
   
8. Create intent: `confirm_item_quantity`
   - **Training phrases**:
     - "2 bottles"
     - "3 pieces"
     - "1 package"
   - **Parameters**:
     - Name: `quantity`
     - Type: `@sys.number`

9. Create intent: `confirm_item_expiry`
   - **Training phrases**:
     - "April 25th"
     - "tomorrow"
     - "next week"
     - "May 1st"
   - **Parameters**:
     - Name: `date`
     - Type: `@sys.date`

### Step 5: Configure Webhook
1. Go to **Develop** → **Webhook**
2. Enter your PC's URL: `http://YOUR_PC_IP:8000/api/voice/webhook`
3. Click **Save**

**Note**: Replace `YOUR_PC_IP` with your actual local IP (e.g., `192.168.1.101`)

### Step 6: Test in Simulator
1. Go to **Test** → **Simulator**
2. Type: "Talk to Fridge Observer"
3. Should connect to your webhook

---

## 💻 Part 3: Backend Setup (Your PC)

### Step 1: Update Environment Variables

Add to your `.env` file:

```bash
# IFTTT Configuration
IFTTT_WEBHOOK_KEY=your_webhook_key_here

# Google Actions Configuration
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_ACTIONS_API_KEY=your_api_key

# Network Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### Step 2: Install Dependencies

```bash
cd /path/to/fridge-observer
pip install -r requirements.txt
```

### Step 3: Apply Database Migration

```bash
# Run the Supabase migration
psql -h your-supabase-host -U postgres -d postgres -f SUPABASE_VOICE_INTEGRATION.sql
```

Or apply via Supabase dashboard:
1. Go to https://app.supabase.com
2. Select your project
3. Go to **SQL Editor**
4. Paste contents of `SUPABASE_VOICE_INTEGRATION.sql`
5. Click **Run**

### Step 4: Find Your PC's Local IP

```bash
# On macOS:
ifconfig | grep "inet " | grep -v 127.0.0.1

# On Linux:
hostname -I

# On Windows:
ipconfig
```

Note your IP (e.g., `192.168.1.101`)

### Step 5: Start FastAPI Server

```bash
# Run on all network interfaces so Raspberry Pi can reach it
uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8000 --reload

# Server will be accessible at:
# - From your PC: http://localhost:8000
# - From Raspberry Pi: http://192.168.1.101:8000
# - From Google Home: http://192.168.1.101:8000
```

### Step 6: Test Endpoints

```bash
# Test pending items endpoint
curl http://localhost:8000/api/voice/pending-items

# Should return: {"items": [], "count": 0}
```

---

## 🍓 Part 4: Raspberry Pi Setup

### Step 1: Install Dependencies on Raspberry Pi

```bash
# SSH into your Raspberry Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
pip3 install opencv-python ultralytics requests python-dotenv

# Install YOLOv8
pip3 install ultralytics
```

### Step 2: Download YOLOv8 Model

```bash
# Download YOLOv8 nano model (smallest, fastest)
cd ~
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# This downloads the model to ~/.cache/ultralytics/
```

### Step 3: Configure Raspberry Pi Script

Create `.env` file on Raspberry Pi:

```bash
nano ~/fridge-observer/.env
```

Add:
```bash
# Your PC's IP address
BACKEND_URL=http://192.168.1.101:8000

# User credentials (get from Supabase)
USER_EMAIL=your_email@example.com
USER_PASSWORD=your_password

# Hardware configuration
LIGHT_SENSOR_PIN=17
DOOR_OPEN_THRESHOLD=50
CAPTURE_FPS=1
```

### Step 4: Copy Raspberry Pi Script

Copy the enhanced `raspberry_pi_sensor.py` to your Raspberry Pi:

```bash
# On your PC
scp raspberry_pi_sensor.py pi@raspberrypi.local:~/fridge-observer/

# On Raspberry Pi
cd ~/fridge-observer
chmod +x raspberry_pi_sensor.py
```

### Step 5: Test Raspberry Pi Script

```bash
# Run manually first to test
python3 raspberry_pi_sensor.py

# You should see:
# "Fridge Observer Sensor Starting..."
# "Connected to backend at http://192.168.1.101:8000"
# "Waiting for door events..."
```

### Step 6: Set Up Auto-Start (Optional)

Create systemd service:

```bash
sudo nano /etc/systemd/system/fridge-observer.service
```

Add:
```ini
[Unit]
Description=Fridge Observer Sensor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/fridge-observer
ExecStart=/usr/bin/python3 /home/pi/fridge-observer/raspberry_pi_sensor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable fridge-observer
sudo systemctl start fridge-observer
sudo systemctl status fridge-observer
```

---

## 🧪 Part 5: Testing the Complete Flow

### Test 1: Manual Trigger (No Hardware)

```bash
# On your PC, simulate Raspberry Pi sending detection results
curl -X POST http://localhost:8000/api/hardware/session-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "session_id": "test_session_001",
    "started_at": "2026-04-18T14:30:00Z",
    "ended_at": "2026-04-18T14:30:20Z",
    "items_added": [
      {
        "name": "Milk",
        "confidence": 0.92,
        "category": "dairy"
      },
      {
        "name": "Eggs",
        "confidence": 0.88,
        "category": "dairy"
      }
    ],
    "items_removed": []
  }'
```

**Expected Result**:
- ✅ Google Home says: *"I detected 2 new items in your fridge..."*
- ✅ Items stored in `pending_items` table
- ✅ Web app shows notification

### Test 2: Voice Interaction

Say to Google Home:
```
You: "Hey Google, talk to Fridge Observer"
Google: "Sure, connecting to Fridge Observer"

You: "What are the pending items?"
Google: "You have 2 pending items: Milk and Eggs. Let's add them. How many Milk?"

You: "2 bottles"
Google: "Got it. What's the expiry date for Milk?"

You: "April 25th"
Google: "Milk added. How many Eggs?"

You: "1 dozen"
Google: "What's the expiry date for Eggs?"

You: "April 30th"
Google: "All items added to your fridge!"
```

### Test 3: Full Hardware Flow

1. **Open fridge door** (light sensor triggers)
2. **Add items** (Milk, Eggs, Chicken)
3. **Close fridge door**
4. **Wait 5-10 seconds** (Raspberry Pi processes frames)
5. **Google Home speaks**: *"I detected 3 new items..."*
6. **Respond with voice** as in Test 2
7. **Check web app** - items should appear in inventory

---

## 🔍 Troubleshooting

### Google Home Not Speaking

**Check IFTTT:**
```bash
# Test webhook manually
curl -X POST https://maker.ifttt.com/trigger/fridge_items_detected/with/key/YOUR_KEY \
  -d '{"value1": "3"}'
```

**Check IFTTT Activity:**
1. Go to https://ifttt.com/activity
2. See if webhook was received
3. Check for errors

### Google Home Not Responding to Questions

**Check webhook URL:**
1. Verify your PC is accessible: `http://YOUR_PC_IP:8000`
2. Test from Raspberry Pi:
   ```bash
   curl http://192.168.1.101:8000/api/voice/pending-items
   ```

**Check Google Actions logs:**
1. Go to https://console.actions.google.com
2. Select your project
3. Go to **Test** → **Logs**

### Raspberry Pi Not Detecting Items

**Check camera:**
```bash
# Test webcam
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL')"
```

**Check YOLOv8:**
```bash
# Test YOLOv8 inference
python3 -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print('Model loaded')"
```

**Check backend connection:**
```bash
# From Raspberry Pi
curl http://192.168.1.101:8000/api/health
```

### Items Not Appearing in Web App

**Check Supabase connection:**
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

**Check database:**
1. Go to Supabase dashboard
2. Table Editor → `pending_items`
3. Verify items are being inserted

**Check WebSocket:**
1. Open browser console (F12)
2. Look for WebSocket connection
3. Should see: `WebSocket connected`

---

## 📱 Part 6: Web App Updates

The web app has been updated with:

### New Features
- ✅ **Pending Items Section** - Shows items waiting for voice input
- ✅ **Real-time Notifications** - Toast notifications when items detected
- ✅ **Voice Status Indicator** - Shows when Google Home is active
- ✅ **Manual Confirmation** - Can add items manually if voice fails

### Access Web App
1. Open browser
2. Go to `http://YOUR_PC_IP:8000`
3. Login with your credentials
4. Navigate to **Inventory** tab
5. See **Pending Items** section at top

---

## 🎉 Success Checklist

- [ ] IFTTT webhook triggers Google Home announcement
- [ ] Google Home responds to "what are the pending items"
- [ ] Google Home asks quantity questions
- [ ] Google Home asks expiry date questions
- [ ] Items appear in web app inventory
- [ ] Raspberry Pi detects door open/close
- [ ] Raspberry Pi captures and processes images
- [ ] YOLOv8 detects food items accurately
- [ ] WebSocket updates web app in real-time
- [ ] Can manually add items if voice fails

---

## 🔐 Security Notes

### Local Network Security
- ✅ All communication on local WiFi (no internet exposure)
- ✅ Supabase handles authentication (JWT tokens)
- ✅ Images never leave your home network
- ✅ Google Home uses OAuth for authentication

### Production Recommendations
- 🔒 Use HTTPS (set up SSL certificate)
- 🔒 Enable firewall on your PC
- 🔒 Use strong Supabase passwords
- 🔒 Rotate IFTTT webhook keys periodically
- 🔒 Keep Raspberry Pi OS updated

---

## 📚 Additional Resources

- [IFTTT Documentation](https://ifttt.com/docs)
- [Google Actions Documentation](https://developers.google.com/assistant)
- [YOLOv8 Documentation](https://docs.ultralytics.com)
- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

---

## 🆘 Support

If you encounter issues:

1. **Check logs**:
   - Raspberry Pi: `journalctl -u fridge-observer -f`
   - FastAPI: Check terminal output
   - Google Actions: Console logs

2. **Test each component individually**:
   - IFTTT webhook
   - Google Actions webhook
   - Raspberry Pi camera
   - YOLOv8 inference
   - Backend endpoints

3. **Common issues**:
   - Firewall blocking connections
   - Wrong IP addresses
   - Expired JWT tokens
   - IFTTT applet disabled
   - Google Home not on same WiFi

---

## 🎯 Next Steps

Once everything is working:

1. **Fine-tune YOLOv8** with your specific food items
2. **Add more voice commands** (remove items, check expiry, etc.)
3. **Set up remote access** (ngrok or Tailscale)
4. **Add mobile app** (React Native or Flutter)
5. **Implement recipe suggestions** based on expiring items

---

**Congratulations! Your Fridge Observer is now voice-enabled!** 🎉
