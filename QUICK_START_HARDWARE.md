# Quick Start - Hardware Integration

Get your smart fridge running in 30 minutes! 🚀

## Prerequisites

- ✅ Raspberry Pi 4 with WiFi configured
- ✅ Logitech Webcam Brio 100 connected
- ✅ Photoresistor circuit wired (GPIO 17)
- ✅ Computer on same WiFi network
- ✅ Fridge Observer server running

## Step 1: Start the Server (5 minutes)

On your computer:

```bash
# Navigate to project
cd fridge-observer

# Activate virtual environment
source .venv/bin/activate  # Mac/Linux
# or
.venv\Scripts\activate  # Windows

# Start server (accessible on network)
python -m uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## Step 2: Get Your API Token (3 minutes)

1. Open browser: `http://localhost:8000`
2. Log in to your account
3. Press **F12** to open DevTools
4. Go to: **Application** → **Cookies** → `http://localhost:8000`
5. Find `fridge_session` cookie
6. **Copy the value** (this is your API token)

## Step 3: Find Your Computer's IP (2 minutes)

**On Mac:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**On Windows:**
```bash
ipconfig
```

**On Linux:**
```bash
hostname -I
```

Example output: `inet 192.168.1.100`

**Write down this IP address!** 📝

## Step 4: Configure Raspberry Pi (10 minutes)

SSH into your Raspberry Pi:

```bash
ssh pi@raspberrypi.local
# Default password: raspberry
```

Create project directory:

```bash
mkdir -p ~/fridge-observer
cd ~/fridge-observer
```

Create `.env` file:

```bash
nano .env
```

Add these lines (replace with YOUR values):

```env
API_BASE_URL=http://192.168.1.100:8000
API_TOKEN=your_jwt_token_here
```

**Important**: Replace `192.168.1.100` with YOUR computer's IP!

Save and exit: **Ctrl+X**, then **Y**, then **Enter**

## Step 5: Install Dependencies (5 minutes)

```bash
# Update system
sudo apt-get update

# Install Python packages
pip3 install requests python-dotenv opencv-python gpiozero

# Test imports
python3 -c "import cv2, requests, gpiozero; print('✅ All packages installed!')"
```

## Step 6: Copy Sensor Script (2 minutes)

On your computer, copy the script to Pi:

```bash
scp raspberry_pi_sensor.py pi@raspberrypi.local:~/fridge-observer/
```

Or manually create it on Pi:

```bash
nano ~/fridge-observer/raspberry_pi_sensor.py
```

Then paste the contents from `raspberry_pi_sensor.py` file.

## Step 7: Test the System (3 minutes)

On Raspberry Pi:

```bash
cd ~/fridge-observer
python3 raspberry_pi_sensor.py
```

You should see:

```
============================================================
Fridge Observer - Hardware Monitor
============================================================
API: http://192.168.1.100:8000
Light sensor: GPIO 17
Threshold: 0.5
Webcam: Index 0
============================================================
Monitoring started... (Press Ctrl+C to stop)
```

## Step 8: Test Door Detection (1 minute)

**Open your fridge door!** 🚪

You should see:

```
🚪 Door OPENED (light: 0.85)
✓ Door event sent: door_opened
📸 Capturing image...
✓ Image uploaded successfully
  Total detected: 2 items
  ✓ Auto-added (1):
    - Apple (expires in 7 days)
  ⏳ Needs expiry input (1):
    - Milk (Google Home will ask)
```

## Step 9: Check Web App (1 minute)

On your computer:

1. Open browser: `http://localhost:8000`
2. Go to **Inventory** page
3. You should see the **Apple** added automatically! 🍎

## Step 10: Test Manual Expiry Input (2 minutes)

For items that need expiry dates (like Milk), you can add them manually:

**Option A: Via Web App**
1. Click "Add Item"
2. Enter: Milk, Dairy, Quantity: 1, Expiry: 2026-04-25
3. Click "Add"

**Option B: Via API (simulating Google Home)**

On your computer:

```bash
curl -X POST http://localhost:8000/api/hardware/add-item-with-expiry \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "Milk",
    "expiry_date": "2026-04-25",
    "quantity": 1
  }'
```

## 🎉 Success!

Your smart fridge is now working! Here's what happens automatically:

1. **You open fridge** → Pi detects via light sensor
2. **Camera captures** → Image uploaded to server
3. **AI detects items** → Gemini identifies food
4. **Fresh items auto-added** → Apples, bananas, etc. with estimated expiry
5. **Web app updates** → See new items instantly
6. **Packaged items** → Add manually or via Google Home (optional)

## Troubleshooting

### "Connection refused" error

**Problem**: Pi can't reach your computer

**Solution**:
```bash
# On Pi, test connection
ping 192.168.1.100  # Use YOUR computer's IP

# If ping fails, check:
# 1. Both devices on same WiFi?
# 2. Firewall blocking port 8000?
# 3. Server running on computer?
```

### "Camera not found" error

**Problem**: Webcam not detected

**Solution**:
```bash
# List video devices
ls -la /dev/video*

# Should see: /dev/video0

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('✅ Camera works!' if cap.isOpened() else '❌ Camera failed')"
```

### "No module named 'gpiozero'" error

**Problem**: Missing Python package

**Solution**:
```bash
pip3 install gpiozero
```

### "Light sensor not responding"

**Problem**: Photoresistor circuit issue

**Solution**:
```bash
# Test GPIO
python3 -c "from gpiozero import LightSensor; s = LightSensor(17); print(f'Light level: {s.value}')"

# Should show value between 0.0 and 1.0
# If error, check wiring:
# - GPIO 17 → Photoresistor → 3.3V
# - GPIO 17 → 10µF Capacitor → GND
```

### Items not appearing in web app

**Problem**: WebSocket not connected or database issue

**Solution**:
1. Refresh web app page
2. Check browser console for errors (F12)
3. Verify item in database:
```bash
# On computer
sqlite3 fridge_observer.db "SELECT * FROM food_items ORDER BY id DESC LIMIT 5;"
```

## Next Steps

### Make it Auto-Start on Boot

```bash
# On Raspberry Pi
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

# Check status
sudo systemctl status fridge-observer

# View logs
sudo journalctl -u fridge-observer -f
```

### Add Google Home (Optional)

See `GOOGLE_HOME_INTEGRATION.md` for voice control setup.

### Monitor System

```bash
# On Pi, check logs
sudo journalctl -u fridge-observer -f

# On computer, check server logs
# (already visible in terminal where server is running)
```

## Usage Tips

### Best Practices

1. **Keep fridge organized** - Camera works best with visible items
2. **Good lighting** - Open door fully for best detection
3. **One item at a time** - Add items individually for accurate detection
4. **Check web app** - Verify items were added correctly

### What Gets Auto-Added

✅ **Fresh fruits**: Apples, bananas, oranges, berries
✅ **Fresh vegetables**: Lettuce, carrots, tomatoes, peppers
✅ **Fresh meat**: Chicken, beef, fish (short expiry)
✅ **Leftovers**: Cooked food (3 days default)

### What Needs Manual Input

⏳ **Packaged dairy**: Milk, yogurt, cheese
⏳ **Beverages**: Juice, soda
⏳ **Packaged goods**: Bread, eggs, condiments

## Performance

- **Detection time**: 3-5 seconds
- **Accuracy**: 85-95% (depends on image quality)
- **Bandwidth**: ~1 MB per door open
- **Battery**: N/A (powered via USB)

## Support

If you encounter issues:

1. Check `HARDWARE_INTEGRATION_STATUS.md` for feature status
2. Read `WIRELESS_SETUP.md` for network troubleshooting
3. See `RASPBERRY_PI_SETUP.md` for hardware details
4. Run `test_hardware_integration.py` to diagnose issues

---

**You're all set! Enjoy your smart fridge! 🎉🍎🥛**
