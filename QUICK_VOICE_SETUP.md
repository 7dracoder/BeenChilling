# Quick Voice Setup Guide

**5-minute setup for Google Home voice integration**

---

## ⚡ Quick Start (3 Steps)

### Step 1: IFTTT Setup (2 minutes)

1. Go to https://ifttt.com/create
2. **IF**: Webhooks → Event: `fridge_items_detected`
3. **THEN**: Google Assistant → Say: `I detected {{Value1}} new items in your fridge`
4. Get your key: https://ifttt.com/maker_webhooks → Documentation
5. Copy the key (looks like: `dA1B2c3D4e5F6g7H8i9J0`)

### Step 2: Configure Backend (1 minute)

Add to `.env`:
```bash
IFTTT_WEBHOOK_KEY=your_key_from_step_1
BACKEND_URL=http://192.168.1.101:8000  # Your PC's IP
```

Find your PC's IP:
```bash
# macOS/Linux:
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows:
ipconfig
```

### Step 3: Apply Database Migration (1 minute)

1. Go to https://app.supabase.com
2. Select your project
3. Go to **SQL Editor**
4. Paste contents of `SUPABASE_VOICE_INTEGRATION.sql`
5. Click **Run**

---

## ✅ Test It

### Test IFTTT:
```bash
curl -X POST https://maker.ifttt.com/trigger/fridge_items_detected/with/key/YOUR_KEY \
  -H "Content-Type: application/json" \
  -d '{"value1": "3"}'
```

**Expected:** Google Home says *"I detected 3 new items in your fridge"*

### Test Backend:
```bash
# Start server
uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8000

# Test endpoint
curl http://localhost:8000/api/voice/pending-items
```

**Expected:** `{"items": [], "count": 0}`

---

## 🎤 Voice Commands

Once set up, you can say:

```
"Hey Google, talk to Fridge Observer"
"What are the pending items?"
"How many Milk?" → "2 bottles"
"Expiry date?" → "April 25th"
```

---

## 📱 Network Setup

**All devices must be on same WiFi:**
- ✅ Raspberry Pi
- ✅ Your PC (running backend)
- ✅ Google Home
- ✅ Your phone/laptop (for web app)

**Firewall:** Allow port 8000 on your PC

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Google Home not speaking | Test IFTTT webhook manually |
| Can't reach backend | Check firewall, verify IP address |
| Items not appearing | Check Supabase migration applied |
| Raspberry Pi can't connect | Verify same WiFi, check BACKEND_URL |

---

## 📚 Full Documentation

For detailed setup including Google Actions:
- See `GOOGLE_HOME_SETUP.md`

For all changes made:
- See `VOICE_INTEGRATION_CHANGES.md`

---

## 🎉 That's It!

Your Fridge Observer now has voice integration!

**Next:** Set up Raspberry Pi following `GOOGLE_HOME_SETUP.md` Part 4
