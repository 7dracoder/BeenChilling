# 🎤 Voice Integration for Fridge Observer

**Hands-free inventory management with Google Home**

---

## What It Does

When you close your fridge door:
1. 📷 Camera detects what you added (Milk, Eggs, Chicken)
2. 🔊 Google Home says: *"I detected 3 new items in your fridge"*
3. 🎤 You say: *"Hey Google, what are the pending items?"*
4. 🗣️ Google Home asks: *"How many Milk?"* → You answer
5. 📱 Items appear in your web app automatically

---

## Quick Start

### 1. Setup (5 minutes)
```bash
# 1. Configure IFTTT (see QUICK_VOICE_SETUP.md)
# 2. Add to .env:
IFTTT_WEBHOOK_KEY=your_key_here
BACKEND_URL=http://YOUR_PC_IP:8000

# 3. Apply database migration
# (Paste SUPABASE_VOICE_INTEGRATION.sql in Supabase SQL Editor)

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start server
uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8000
```

### 2. Test
```bash
# Test IFTTT
curl -X POST https://maker.ifttt.com/trigger/fridge_items_detected/with/key/YOUR_KEY \
  -d '{"value1": "3"}'

# Google Home should speak!
```

---

## Documentation

| File | What It's For |
|------|---------------|
| **QUICK_VOICE_SETUP.md** | 5-minute setup guide |
| **GOOGLE_HOME_SETUP.md** | Complete setup (60+ pages) |
| **VOICE_INTEGRATION_CHANGES.md** | Technical changes |
| **IMPLEMENTATION_COMPLETE.md** | Feature summary |

---

## Architecture

```
Raspberry Pi → Your PC → IFTTT → Google Home
     ↓            ↓                    ↓
  YOLOv8      FastAPI              Voice UI
  Webcam      Supabase             Questions
  Sensor      WebSocket            Answers
```

---

## Requirements

- ✅ Raspberry Pi 4 (2GB+ RAM)
- ✅ Logitech Webcam
- ✅ Google Home device
- ✅ Your PC (running backend)
- ✅ All on same WiFi network

---

## Features

- ✅ Automatic voice notifications
- ✅ Smart quantity questions (always asked)
- ✅ Smart expiry questions (only for packaged items)
- ✅ Real-time web app updates
- ✅ Voice interaction history
- ✅ Session analytics

---

## API Endpoints

```
GET  /api/voice/pending-items      # Fetch pending items
POST /api/voice/confirm-item       # Confirm with quantity/expiry
POST /api/hardware/session-complete # Receive detection results
```

---

## Database Tables

- `pending_items` - Items waiting for voice input
- `capture_sessions` - Door open/close tracking
- `voice_interactions` - Voice command logging

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Google Home not speaking | Test IFTTT webhook |
| Can't reach backend | Check firewall, IP address |
| Items not appearing | Check database migration |

---

## Next Steps

1. ✅ **Quick setup** → `QUICK_VOICE_SETUP.md`
2. 📚 **Full setup** → `GOOGLE_HOME_SETUP.md`
3. 🔧 **Configure Raspberry Pi** → Part 4 of setup guide
4. 🧪 **Test complete flow** → End-to-end testing

---

## Support

- 📖 Read `GOOGLE_HOME_SETUP.md` for detailed instructions
- 🐛 Check `VOICE_INTEGRATION_CHANGES.md` for technical details
- 💬 Review troubleshooting section in setup guide

---

**Ready to get started?** → Open `QUICK_VOICE_SETUP.md`
