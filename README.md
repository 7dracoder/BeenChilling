# BeenChilling

A smart fridge management web app that tracks your food inventory, reduces waste, and generates AI-powered recipes based on what you have.

Live at: www.beenchilling.club

---

## Access

Visit www.beenchilling.club and create a free account with your email and password. A 6-digit verification code will be sent to your email to confirm your account.

---

## Features

- Food inventory tracking with expiry date monitoring
- AI-generated recipes based on items in your fridge, prioritizing items expiring soon
- Expiry alerts and notifications
- EcoScan product blueprint generation
- AI assistant for food storage tips and questions
- Real-time updates via WebSocket
- Raspberry Pi hardware integration for automatic food detection

---

## Tech Stack

**Backend**
- Python 3.11
- FastAPI — REST API and WebSocket server
- Supabase — PostgreSQL database and authentication
- K2-Think API — AI reasoning for recipe generation and assistant
- Gemini Imagen API — Blueprint image generation
- Gmail SMTP — OTP email verification

**Frontend**
- Vanilla JavaScript, HTML5, CSS3
- WebSocket client for real-time inventory updates

**Infrastructure**
- Render.com — Web hosting (free tier)
- Supabase — Managed PostgreSQL (free tier)

**Hardware**
- Raspberry Pi 4 (or 3B+)
- USB webcam or Raspberry Pi Camera Module v2
- Light-dependent resistor (LDR) for fridge door detection
- GPIO wiring for sensor input

---

## Hardware Setup

The Raspberry Pi sits inside or near the fridge and detects when the door opens using an LDR sensor. When the door opens, it captures an image with the camera and sends it to the backend, where Gemini Vision identifies the food items and updates the inventory automatically.

Components needed:
- Raspberry Pi 4 (2GB RAM minimum)
- Camera Module v2 or USB webcam
- LDR sensor + 10k ohm resistor
- Jumper wires and breadboard
- MicroSD card (16GB+)

---

## Local Installation

**Requirements:** Python 3.11+, a Supabase account, and the environment variables below.

```bash
git clone https://github.com/7dracoder/BeenChilling.git
cd BeenChilling
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your credentials in .env
uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

---

## Environment Variables

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
GEMINI_API_KEY=your_gemini_key
K2_API_KEY=your_k2_key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your@gmail.com
```

---

## Database Setup

Run the migrations in order against your Supabase project:

```
supabase/migrations/20260418000001_initial_schema.sql
supabase/migrations/20260418000002_email_otps.sql
```

---

## License

MIT
