# Raspberry Pi Hardware Setup Guide

## Hardware Components

- **1x Raspberry Pi 4 Model B** - Main controller
- **1x Photoresistor** - Light sensor for door detection
- **1x 10µF Capacitor** - For RC circuit timing
- **1x Protoboard Mini** - For circuit assembly
- **1x Logitech Webcam Brio 100 1080p** - For capturing fridge contents
- **1x Google Home Mini** - For voice notifications (optional)
- **3x Jumper Wires (Male to Female)** - For connections

## Circuit Diagram

### Photoresistor RC Circuit

```
GPIO 17 ────┬──── Photoresistor ──── 3.3V
            │
            └──── 10µF Capacitor ──── GND
```

**Connections:**
1. **GPIO 17** → One leg of photoresistor
2. **Photoresistor** (other leg) → **3.3V** power
3. **GPIO 17** → Positive leg of 10µF capacitor
4. **Capacitor** (negative leg) → **GND**

## Software Setup

### 1. Install Raspberry Pi OS

```bash
# Update system
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages

```bash
# Install Python dependencies
sudo apt install -y python3-pip python3-opencv python3-gpiozero

# Install Python packages
pip3 install requests python-dotenv opencv-python
```

### 3. Configure Webcam

```bash
# Test webcam
v4l2-ctl --list-devices

# Set permissions
sudo usermod -a -G video $USER
```

### 4. Setup Fridge Observer Script

```bash
# Create project directory
mkdir -p ~/fridge-observer
cd ~/fridge-observer

# Copy the sensor script
# (Transfer raspberry_pi_sensor.py to this directory)

# Create .env file
nano .env
```

Add to `.env`:
```env
API_BASE_URL=http://YOUR_SERVER_IP:8000
API_TOKEN=your_jwt_token_here
```

### 5. Get Your API Token

1. Open web app: `http://YOUR_SERVER_IP:8000`
2. Log in to your account
3. Open browser DevTools (F12)
4. Go to Application → Cookies
5. Copy the `fridge_session` cookie value
6. Paste it as `API_TOKEN` in `.env`

### 6. Test the Script

```bash
# Make script executable
chmod +x raspberry_pi_sensor.py

# Run test
python3 raspberry_pi_sensor.py
```

You should see:
```
============================================================
Fridge Observer - Hardware Monitor
============================================================
API: http://YOUR_SERVER_IP:8000
Light sensor: GPIO 17
Threshold: 0.5
Webcam: Index 0
============================================================
Monitoring started... (Press Ctrl+C to stop)
```

### 7. Setup Auto-Start on Boot

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

## How It Works

### 1. **Door Detection**
- Photoresistor measures light level
- When door opens, light increases
- RC circuit provides stable readings
- Threshold: 0.5 (adjustable)

### 2. **Image Capture**
- Door opens → Wait 2 seconds
- Webcam captures 1080p image
- Image uploaded to server
- AI analyzes and detects food items

### 3. **Data Flow**

```
Raspberry Pi                    Web Server
    │                               │
    ├─ Door Opens ─────────────────>│ POST /api/hardware/door-event
    │                               │
    ├─ Capture Image ──────────────>│ POST /api/hardware/capture-image
    │                               │   └─> AI Detection
    │                               │   └─> Add to Inventory
    │                               │
    ├─ Door Closes ────────────────>│ POST /api/hardware/door-event
    │                               │
    └─ Status Update (every 5min) ─>│ POST /api/hardware/status
```

### 4. **Web App Updates**

The web app receives:
- **Door events**: Real-time notifications when door opens/closes
- **New items**: Automatically added to inventory
- **Hardware status**: Monitor sensor health

## Troubleshooting

### Webcam Not Detected
```bash
# List video devices
ls -l /dev/video*

# Test with fswebcam
sudo apt install fswebcam
fswebcam test.jpg
```

### Light Sensor Not Working
```bash
# Test GPIO
python3 -c "from gpiozero import LightSensor; s = LightSensor(17); print(s.value)"
```

### API Connection Failed
```bash
# Test API connectivity
curl http://YOUR_SERVER_IP:8000/api/health

# Check token
echo $API_TOKEN
```

### Adjust Light Threshold
Edit `raspberry_pi_sensor.py`:
```python
LIGHT_THRESHOLD = 0.3  # Lower = more sensitive
```

## Google Home Integration (Optional)

To enable voice notifications:

1. Install Google Assistant SDK
2. Configure voice commands
3. Trigger notifications when items expire

(Detailed guide coming soon)

## Next Steps

1. ✅ Wire up the circuit on protoboard
2. ✅ Install software on Raspberry Pi
3. ✅ Test door detection
4. ✅ Test image capture
5. ✅ Setup auto-start service
6. ✅ Mount hardware inside/near fridge

## Support

If you encounter issues:
1. Check system logs: `sudo journalctl -u fridge-observer -f`
2. Test components individually
3. Verify API connectivity
4. Check GPIO pin numbers match your wiring

---

**Your hardware is now integrated with the Fridge Observer web app!** 🎉
