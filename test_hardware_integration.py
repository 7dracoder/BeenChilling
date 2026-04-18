#!/usr/bin/env python3
"""
Test script for hardware integration
Tests the complete workflow: door event → image capture → AI detection → inventory update
"""
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")

if not API_TOKEN:
    print("❌ Error: API_TOKEN not set in .env file")
    print("Please add your JWT token to .env:")
    print("API_TOKEN=your_jwt_token_here")
    exit(1)

headers = {"Authorization": f"Bearer {API_TOKEN}"}


def test_door_event():
    """Test door open/close event"""
    print("\n" + "="*60)
    print("TEST 1: Door Event")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE_URL}/api/hardware/door-event",
        json={
            "event": "door_opened",
            "timestamp": "2026-04-18T14:30:00Z",
            "light_level": 0.85
        },
        headers=headers
    )
    
    if response.ok:
        print("✅ Door event sent successfully")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Error: {response.text}")
    
    return response.ok


def test_image_capture():
    """Test image capture with AI detection"""
    print("\n" + "="*60)
    print("TEST 2: Image Capture & AI Detection")
    print("="*60)
    
    # Create a test image (or use existing one)
    test_image_path = "test_fridge_image.jpg"
    
    if not Path(test_image_path).exists():
        print(f"⚠️  Test image not found: {test_image_path}")
        print("Creating a placeholder image...")
        
        # Create a simple test image using PIL
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw some text
            draw.text((50, 50), "Test Fridge Image", fill='black')
            draw.text((50, 100), "Apple", fill='red')
            draw.text((50, 150), "Milk", fill='blue')
            draw.text((50, 200), "Banana", fill='yellow')
            
            img.save(test_image_path)
            print(f"✅ Created test image: {test_image_path}")
        except ImportError:
            print("❌ PIL not installed. Please provide a test image or install Pillow:")
            print("pip install Pillow")
            return False
    
    # Upload image
    with open(test_image_path, 'rb') as f:
        files = {'image': ('fridge.jpg', f, 'image/jpeg')}
        response = requests.post(
            f"{API_BASE_URL}/api/hardware/capture-image",
            files=files,
            headers=headers
        )
    
    if response.ok:
        result = response.json()
        print("✅ Image processed successfully")
        print(f"\nTotal items detected: {result['total_items']}")
        
        if result['auto_added']:
            print(f"\n✅ Auto-added items ({len(result['auto_added'])}):")
            for item in result['auto_added']:
                print(f"  - {item['name']} ({item['category']})")
                print(f"    Expires: {item['expiry_date']} ({item['estimated_days']} days)")
        
        if result['needs_expiry_input']:
            print(f"\n⏳ Items needing expiry input ({len(result['needs_expiry_input'])}):")
            for item in result['needs_expiry_input']:
                print(f"  - {item['name']} ({item['category']})")
                print(f"    Confidence: {item['confidence']:.2f}")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False


def test_add_expiry():
    """Test adding item with expiry date (Google Home simulation)"""
    print("\n" + "="*60)
    print("TEST 3: Add Item with Expiry (Google Home)")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE_URL}/api/hardware/add-item-with-expiry",
        json={
            "item_name": "Milk",
            "expiry_date": "2026-04-25",
            "quantity": 1
        },
        headers=headers
    )
    
    if response.ok:
        result = response.json()
        print("✅ Item added successfully")
        print(f"Item: {result['item']}")
        print(f"Expiry: {result['expiry_date']}")
        print(f"Quantity: {result['quantity']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Error: {response.text}")
    
    return response.ok


def test_hardware_status():
    """Test hardware status endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Hardware Status")
    print("="*60)
    
    # Send status
    response = requests.post(
        f"{API_BASE_URL}/api/hardware/status",
        json={
            "light_level": 0.75,
            "last_capture": "2026-04-18T14:30:00Z",
            "status": "online",
            "timestamp": "2026-04-18T14:35:00Z"
        },
        headers=headers
    )
    
    if response.ok:
        print("✅ Status sent successfully")
    else:
        print(f"❌ Failed to send status: {response.status_code}")
    
    # Get status
    response = requests.get(
        f"{API_BASE_URL}/api/hardware/status",
        headers=headers
    )
    
    if response.ok:
        result = response.json()
        print("✅ Status retrieved successfully")
        print(f"Status: {result['status']}")
        print(f"Light level: {result['light_level']}")
        print(f"Last capture: {result['last_capture']}")
    else:
        print(f"❌ Failed to get status: {response.status_code}")
    
    return response.ok


def main():
    """Run all tests"""
    print("="*60)
    print("Hardware Integration Test Suite")
    print("="*60)
    print(f"API: {API_BASE_URL}")
    print(f"Token: {'✅ Set' if API_TOKEN else '❌ Not set'}")
    
    results = []
    
    # Run tests
    results.append(("Door Event", test_door_event()))
    results.append(("Image Capture", test_image_capture()))
    results.append(("Add Expiry", test_add_expiry()))
    results.append(("Hardware Status", test_hardware_status()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Hardware integration is working!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")


if __name__ == "__main__":
    main()
