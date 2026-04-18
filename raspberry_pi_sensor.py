#!/usr/bin/env python3
"""
Raspberry Pi Fridge Observer - Hardware Integration Script
Monitors fridge door using photoresistor and captures images with webcam
"""
import time
import requests
import cv2
from gpiozero import LightSensor
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")  # Your JWT token
LIGHT_SENSOR_PIN = 17  # GPIO pin for photoresistor (adjust as needed)
LIGHT_THRESHOLD = 0.5  # Threshold for door open detection (0-1)
CAPTURE_DELAY = 2  # Seconds to wait after door opens before capturing
WEBCAM_INDEX = 0  # Usually 0 for first webcam

# Initialize hardware
light_sensor = LightSensor(LIGHT_SENSOR_PIN)
camera = cv2.VideoCapture(WEBCAM_INDEX)

# Set camera resolution
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# State tracking
door_was_open = False
last_capture_time = 0
CAPTURE_COOLDOWN = 30  # Minimum seconds between captures


def send_door_event(event_type):
    """Send door open/close event to API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/hardware/door-event",
            json={
                "event": event_type,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "light_level": light_sensor.value
            },
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            timeout=5
        )
        if response.ok:
            print(f"✓ Door event sent: {event_type}")
        else:
            print(f"✗ Failed to send door event: {response.status_code}")
    except Exception as e:
        print(f"✗ Error sending door event: {e}")


def capture_and_upload_image():
    """Capture image from webcam and upload to API"""
    global last_capture_time
    
    # Check cooldown
    current_time = time.time()
    if current_time - last_capture_time < CAPTURE_COOLDOWN:
        print(f"⏳ Capture cooldown active ({CAPTURE_COOLDOWN}s)")
        return
    
    try:
        # Capture frame
        ret, frame = camera.read()
        if not ret:
            print("✗ Failed to capture image from webcam")
            return
        
        # Save to temporary file
        temp_file = "/tmp/fridge_capture.jpg"
        cv2.imwrite(temp_file, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        
        # Upload to API
        with open(temp_file, 'rb') as f:
            files = {'image': ('fridge.jpg', f, 'image/jpeg')}
            response = requests.post(
                f"{API_BASE_URL}/api/hardware/capture-image",
                files=files,
                headers={"Authorization": f"Bearer {API_TOKEN}"},
                timeout=30
            )
        
        if response.ok:
            result = response.json()
            print(f"✓ Image uploaded successfully")
            
            # Show detected items
            total = result.get('total_items', 0)
            needs_expiry = result.get('needs_expiry_input', [])
            auto_added = result.get('auto_added', [])
            
            print(f"  Total detected: {total} items")
            
            if auto_added:
                print(f"  ✓ Auto-added ({len(auto_added)}):")
                for item in auto_added:
                    print(f"    - {item['name']} (expires in {item['estimated_expiry_days']} days)")
            
            if needs_expiry:
                print(f"  ⏳ Needs expiry input ({len(needs_expiry)}):")
                for item in needs_expiry:
                    print(f"    - {item['name']} (Google Home will ask)")
                print(f"  → Google Home will now ask for expiry dates")
            
            last_capture_time = current_time
        else:
            print(f"✗ Failed to upload image: {response.status_code}")
            
        # Clean up
        os.remove(temp_file)
        
    except Exception as e:
        print(f"✗ Error capturing/uploading image: {e}")


def send_status_update():
    """Send hardware status to API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/hardware/status",
            json={
                "light_level": light_sensor.value,
                "last_capture": datetime.fromtimestamp(last_capture_time).isoformat() if last_capture_time > 0 else None,
                "status": "online",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            timeout=5
        )
        if response.ok:
            print("✓ Status update sent")
    except Exception as e:
        print(f"✗ Error sending status: {e}")


def main():
    """Main monitoring loop"""
    global door_was_open
    
    print("=" * 60)
    print("Fridge Observer - Hardware Monitor")
    print("=" * 60)
    print(f"API: {API_BASE_URL}")
    print(f"Light sensor: GPIO {LIGHT_SENSOR_PIN}")
    print(f"Threshold: {LIGHT_THRESHOLD}")
    print(f"Webcam: Index {WEBCAM_INDEX}")
    print("=" * 60)
    print("Monitoring started... (Press Ctrl+C to stop)")
    print()
    
    last_status_time = 0
    STATUS_INTERVAL = 300  # Send status every 5 minutes
    
    try:
        while True:
            # Read light sensor
            light_value = light_sensor.value
            door_is_open = light_value > LIGHT_THRESHOLD
            
            # Detect door state change
            if door_is_open and not door_was_open:
                # Door just opened
                print(f"\n🚪 Door OPENED (light: {light_value:.2f})")
                send_door_event("door_opened")
                
                # Wait a moment for door to fully open
                time.sleep(CAPTURE_DELAY)
                
                # Capture and upload image
                print("📸 Capturing image...")
                capture_and_upload_image()
                
                door_was_open = True
                
            elif not door_is_open and door_was_open:
                # Door just closed
                print(f"\n🚪 Door CLOSED (light: {light_value:.2f})")
                send_door_event("door_closed")
                door_was_open = False
            
            # Send periodic status updates
            current_time = time.time()
            if current_time - last_status_time > STATUS_INTERVAL:
                send_status_update()
                last_status_time = current_time
            
            # Small delay to avoid excessive CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n⏹ Stopping monitor...")
    finally:
        # Cleanup
        camera.release()
        print("✓ Camera released")
        print("✓ Monitor stopped")


if __name__ == "__main__":
    main()
