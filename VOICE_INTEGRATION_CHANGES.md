# Voice Integration Changes Summary

This document summarizes all changes made to add Google Home voice integration to the Fridge Observer system.

---

## 📁 New Files Created

### 1. `GOOGLE_HOME_SETUP.md`
Complete setup guide with step-by-step instructions for:
- IFTTT configuration
- Google Actions setup
- Backend configuration
- Raspberry Pi setup
- Testing procedures
- Troubleshooting guide

### 2. `SUPABASE_VOICE_INTEGRATION.sql`
Database migration that adds:
- `pending_items` table - Items waiting for voice confirmation
- `capture_sessions` table - Door open/close session tracking
- `voice_interactions` table - Voice command logging
- Helper functions for managing pending items
- Row-level security policies
- Realtime subscriptions

### 3. `fridge_observer/routers/voice.py`
New API router with endpoints:
- `GET /api/voice/pending-items` - Fetch items waiting for voice input
- `POST /api/voice/confirm-item` - Confirm item with quantity/expiry
- `DELETE /api/voice/pending-items/{id}` - Remove pending item
- `POST /api/voice/webhook` - Google Actions webhook handler
- `GET /api/voice/stats` - Voice interaction statistics

### 4. `VOICE_INTEGRATION_CHANGES.md` (this file)
Summary of all changes made

---

## 🔧 Modified Files

### 1. `fridge_observer/main.py`
**Changes:**
- Added import for `voice_router`
- Registered voice router: `app.include_router(voice_router.router)`

**Lines changed:** 2 additions

### 2. `fridge_observer/routers/hardware.py`
**Changes:**
- Added `Dict, Any` to type imports
- Added `ExpiryDateInput` model
- Added `CaptureSessionComplete` model
- Added `POST /api/hardware/session-complete` endpoint
  - Receives processed detection results from Raspberry Pi
  - Stores capture session metadata
  - Classifies items (packaged vs fresh)
  - Creates pending items
  - Triggers IFTTT notification
  - Broadcasts WebSocket update

**Lines changed:** ~150 additions

### 3. `requirements.txt`
**Changes:**
- Added `python-dateutil==2.9.0` for date parsing

**Lines changed:** 1 addition

### 4. `.env.example`
**Changes:**
- Added `IFTTT_WEBHOOK_KEY` configuration
- Added `GOOGLE_PROJECT_ID` configuration
- Added `GOOGLE_ACTIONS_API_KEY` configuration
- Added `BACKEND_HOST`, `BACKEND_PORT`, `BACKEND_URL` for network setup

**Lines changed:** 7 additions

---

## 🗄️ Database Changes

### New Tables

#### `pending_items`
Stores items detected by camera that are waiting for user voice confirmation.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to auth.users
- `session_id` - Links to capture session
- `item_name` - Name of detected item
- `category` - Food category
- `confidence` - Detection confidence (0-1)
- `is_packaged` - Whether item needs expiry input
- `estimated_expiry_days` - Auto-estimated expiry for fresh items
- `needs_quantity` - Always true (Google Home asks)
- `needs_expiry_date` - True for packaged items only
- `thumbnail` - Optional image thumbnail
- `created_at` - Timestamp
- `expires_at` - Auto-expires after 24 hours

#### `capture_sessions`
Tracks each door open/close session for analytics.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to auth.users
- `session_id` - Unique session identifier
- `started_at` - Door opened timestamp
- `ended_at` - Door closed timestamp
- `duration_seconds` - Session duration
- `frames_captured` - Number of frames processed
- `items_detected` - Total items detected
- `items_added` - Items added to fridge
- `items_removed` - Items removed from fridge
- `status` - processing/completed/failed
- `created_at` - Timestamp

#### `voice_interactions`
Logs all voice interactions for debugging and analytics.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to auth.users
- `session_id` - Optional session link
- `intent` - Google Actions intent name
- `query` - User's voice query
- `response` - System response
- `success` - Whether interaction succeeded
- `error_message` - Error details if failed
- `created_at` - Timestamp

### New Functions

#### `cleanup_expired_pending_items()`
Automatically deletes pending items older than 24 hours.

#### `get_pending_items_count(p_user_id)`
Returns count of pending items for a user.

#### `confirm_pending_item(p_pending_item_id, p_quantity, p_expiry_date)`
Moves a pending item to the inventory table with user-provided details.

---

## 🔄 Complete Flow

### 1. Door Opens
```
Light sensor detects → Raspberry Pi starts capturing frames (1 fps)
```

### 2. Door Closes
```
Light sensor detects → Raspberry Pi processes all frames with YOLOv8
→ Aggregates detections across frames
→ Compares before/after inventory
→ Sends results to backend
```

### 3. Backend Processing
```
POST /api/hardware/session-complete
→ Stores capture session
→ Classifies each item (packaged vs fresh)
→ Creates pending items in database
→ Triggers IFTTT webhook
→ Broadcasts WebSocket update
```

### 4. Google Home Notification
```
IFTTT receives webhook
→ Google Home speaks: "I detected 3 new items in your fridge"
```

### 5. User Voice Interaction
```
User: "Hey Google, what are the pending items?"
→ GET /api/voice/pending-items

Google Home: "You have 3 items: Milk, Eggs, Chicken. How many Milk?"
User: "2 bottles"

Google Home: "Expiry date for Milk?"
User: "April 25th"

→ POST /api/voice/confirm-item
→ Item added to inventory
→ WebSocket broadcast to web app
→ Google Home: "Milk added"
```

### 6. Web App Update
```
WebSocket receives update
→ Inventory refreshes in real-time
→ Pending items section updates
→ Toast notification appears
```

---

## 🌐 API Endpoints Summary

### Voice Endpoints (`/api/voice/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/voice/pending-items` | Get all pending items | Yes |
| POST | `/api/voice/confirm-item` | Confirm item with quantity/expiry | Yes |
| DELETE | `/api/voice/pending-items/{id}` | Remove pending item | Yes |
| POST | `/api/voice/webhook` | Google Actions webhook | No |
| GET | `/api/voice/stats` | Voice interaction statistics | Yes |

### Hardware Endpoints (`/api/hardware/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/hardware/session-complete` | Receive processed session results | Yes |
| POST | `/api/hardware/door-event` | Door open/close event | Yes |
| POST | `/api/hardware/capture-image` | Single image capture (legacy) | Yes |
| GET | `/api/hardware/status` | Hardware status | Yes |

---

## 🔐 Environment Variables

### Required for Voice Integration

```bash
# IFTTT Configuration (for Google Home notifications)
IFTTT_WEBHOOK_KEY=your_ifttt_webhook_key_here

# Google Actions Configuration (for voice commands)
GOOGLE_PROJECT_ID=your_google_cloud_project_id
GOOGLE_ACTIONS_API_KEY=your_google_actions_api_key

# Network Configuration (for local WiFi)
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_URL=http://192.168.1.101:8000  # Your PC's local IP
```

---

## 📦 Dependencies Added

```
python-dateutil==2.9.0  # For flexible date parsing
```

---

## 🧪 Testing Checklist

### Backend Tests
- [ ] `GET /api/voice/pending-items` returns empty list initially
- [ ] `POST /api/hardware/session-complete` creates pending items
- [ ] `POST /api/voice/confirm-item` moves item to inventory
- [ ] `DELETE /api/voice/pending-items/{id}` removes item
- [ ] WebSocket broadcasts work correctly
- [ ] IFTTT webhook triggers successfully

### Integration Tests
- [ ] Raspberry Pi can reach backend endpoint
- [ ] IFTTT webhook triggers Google Home
- [ ] Google Home can fetch pending items
- [ ] Google Home can submit confirmations
- [ ] Web app receives real-time updates
- [ ] Database migrations apply successfully

### End-to-End Tests
- [ ] Open fridge → items detected → Google Home speaks
- [ ] Voice interaction completes successfully
- [ ] Items appear in web app inventory
- [ ] Pending items expire after 24 hours
- [ ] Multiple users don't see each other's items

---

## 🚀 Deployment Steps

### 1. Apply Database Migration
```bash
# Via Supabase dashboard
1. Go to SQL Editor
2. Paste SUPABASE_VOICE_INTEGRATION.sql
3. Click Run

# Or via psql
psql -h your-supabase-host -U postgres -d postgres -f SUPABASE_VOICE_INTEGRATION.sql
```

### 2. Update Environment Variables
```bash
# Add to .env file
IFTTT_WEBHOOK_KEY=your_key_here
GOOGLE_PROJECT_ID=your_project_id
BACKEND_URL=http://YOUR_PC_IP:8000
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Restart Backend
```bash
uvicorn fridge_observer.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Configure IFTTT
Follow steps in `GOOGLE_HOME_SETUP.md`

### 6. Configure Google Actions
Follow steps in `GOOGLE_HOME_SETUP.md`

### 7. Test
```bash
# Test IFTTT
curl -X POST https://maker.ifttt.com/trigger/fridge_items_detected/with/key/YOUR_KEY \
  -d '{"value1": "3"}'

# Test pending items endpoint
curl http://localhost:8000/api/voice/pending-items \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 📊 Monitoring

### Logs to Watch

**Backend logs:**
```bash
# Watch for:
- "IFTTT notification sent for X items"
- "Item confirmed via voice: X"
- "Received session complete: X"
```

**Supabase logs:**
```sql
-- Check pending items
SELECT * FROM pending_items WHERE user_id = 'your_user_id';

-- Check voice interactions
SELECT * FROM voice_interactions ORDER BY created_at DESC LIMIT 10;

-- Check capture sessions
SELECT * FROM capture_sessions ORDER BY created_at DESC LIMIT 10;
```

**IFTTT Activity:**
- Go to https://ifttt.com/activity
- Check webhook triggers

**Google Actions Logs:**
- Go to https://console.actions.google.com
- Select project → Test → Logs

---

## 🐛 Common Issues

### Google Home Not Speaking
**Solution:** Check IFTTT webhook key and test manually

### Google Home Not Responding to Questions
**Solution:** Verify webhook URL in Google Actions points to your PC's IP

### Items Not Appearing in Web App
**Solution:** Check WebSocket connection in browser console

### Raspberry Pi Can't Reach Backend
**Solution:** Verify all devices on same WiFi and firewall allows port 8000

---

## 🎯 Next Steps

1. **Fine-tune YOLOv8** with your specific food items
2. **Add more voice commands**:
   - "Remove item from fridge"
   - "What's expiring soon?"
   - "Show me recipes"
3. **Implement conversation state** for multi-turn dialogs
4. **Add voice feedback** for errors
5. **Create mobile app** for remote access
6. **Add analytics dashboard** for voice usage

---

## 📚 Related Documentation

- `GOOGLE_HOME_SETUP.md` - Complete setup guide
- `SUPABASE_VOICE_INTEGRATION.sql` - Database schema
- `.kiro/specs/fridge-observer/design.md` - System design
- `.kiro/specs/fridge-observer/requirements.md` - Requirements

---

**All changes are backward compatible** - existing functionality continues to work without voice integration enabled.
