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

Backend: FastAPI, Python 3.11, Supabase
Frontend: HTML, CSS, JavaScript
AI: Google Gemini Vision, Replicate
Hardware: Raspberry Pi 4, OpenCV, GPIO sensors
Deployment: Digital Ocean (backend), Vercel (frontend)

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your API keys
4. Run the server: `python -m uvicorn fridge_observer.main:app --reload`
5. Open http://localhost:8000

## Hardware Setup

You'll need:
- Raspberry Pi 4
- USB webcam (1080p recommended)
- Photoresistor and 10µF capacitor for door detection
- Protoboard and jumper wires

Total cost is around $70-110. Setup takes about 30 minutes following the hardware guide.

## Deployment

The backend deploys to Digital Ocean (around $12/month) and the frontend to Vercel (free tier). Both have detailed deployment guides in the docs folder.

After deployment, update your Raspberry Pi's `.env` file to point to your production API URL instead of localhost.

## Documentation

- `QUICK_START_HARDWARE.md` - Hardware setup guide
- `DEPLOYMENT_DIGITAL_OCEAN.md` - Backend deployment
- `DEPLOYMENT_VERCEL.md` - Frontend deployment
- `RASPBERRY_PI_SETUP.md` - Detailed Pi configuration
- `HARDWARE_INTEGRATION_STATUS.md` - Current feature status

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

## Testing

Run the hardware integration tests:
```bash
python test_hardware_integration.py
```

## License

MIT License - see LICENSE file

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
