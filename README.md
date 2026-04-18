# ClearChill

A smart fridge management system that uses AI to automatically track your food inventory and reduce waste.

## What It Does

ClearChill monitors your fridge using a Raspberry Pi with a camera and light sensor. When you open the door, it captures an image, identifies the food items using AI, and updates your inventory automatically. Most items get expiry dates estimated automatically, so you always know what needs to be used soon.

## Features

- Automatic food detection using Google Gemini Vision AI
- Smart expiry date estimation for fresh produce
- Real-time inventory updates via WebSocket
- Web dashboard to view your inventory from anywhere
- Raspberry Pi hardware integration with door sensor and camera
- AI-generated sustainability insights and blueprints
- Optional voice input for packaged items

## Tech Stack

**Backend**: FastAPI, Python 3.11, Supabase (auth + database)
**Frontend**: HTML, CSS, JavaScript
**AI**: Google Gemini Vision, Replicate
**Hardware**: Raspberry Pi 4, OpenCV, GPIO sensors
**Deployment**: Digital Ocean (all-in-one)

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/7dracoder/ClearChill.git
cd ClearChill
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
nano .env
```

Required:
- `SUPABASE_URL` and `SUPABASE_KEY` - Get from [Supabase](https://supabase.com)
- `GEMINI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `REPLICATE_API_TOKEN` - Get from [Replicate](https://replicate.com)
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`

### 3. Run Locally

```bash
python -m uvicorn fridge_observer.main:app --reload
```

Open http://localhost:8000

## Deployment

Deploy everything (backend + frontend + database) to Digital Ocean in 30 minutes:

```bash
# Follow the quick deployment guide
cat QUICK_DEPLOY.md
```

**Cost**: $18/month for everything (4GB RAM droplet recommended)

## Hardware Setup

You'll need:
- Raspberry Pi 4
- USB webcam (1080p recommended)
- Photoresistor and 10µF capacitor for door detection
- Protoboard and jumper wires

Total cost: $70-110. Setup takes about 30 minutes.

See `RASPBERRY_PI_SETUP.md` for detailed instructions.

## How It Works

1. You open your fridge door
2. Light sensor detects the door opening
3. Camera captures an image after 2 seconds
4. Image is sent to your server via WiFi
5. Gemini AI identifies the food items
6. Fresh items get automatic expiry estimates
7. Items are added to your inventory database
8. Web app updates in real-time via WebSocket

The whole process takes about 5-6 seconds from door open to seeing items in your app.

## Testing Hardware Integration

```bash
python test_hardware_integration.py
```

## Documentation

- `QUICK_DEPLOY.md` - 30-minute deployment guide for Digital Ocean
- `RASPBERRY_PI_SETUP.md` - Hardware setup and configuration
- `.env.example` - Environment variables reference

## License

MIT License - see LICENSE file

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
