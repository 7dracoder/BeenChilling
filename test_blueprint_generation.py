#!/usr/bin/env python3
"""
Test script to diagnose blueprint image generation issues.
Run this to see which AI service is being used and why.
"""
import asyncio
import os
import sys

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_blueprint():
    from fridge_observer.image_gen import generate_blueprint_image
    
    print("=" * 60)
    print("BLUEPRINT GENERATION TEST")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    hf_token = os.environ.get("HF_TOKEN", "")
    cf_key = os.environ.get("CLOUDFLARE_API_KEY", "")
    cf_account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    
    print(f"   HF_TOKEN: {'✓ Configured' if hf_token and len(hf_token) > 10 else '✗ Not configured'}")
    if hf_token:
        print(f"   HF_TOKEN value: {hf_token[:10]}...{hf_token[-5:]}")
    
    print(f"   CLOUDFLARE_API_KEY: {'✓ Configured' if cf_key and 'your-cloudflare' not in cf_key.lower() else '✗ Not configured (placeholder)'}")
    if cf_key and 'your-cloudflare' not in cf_key.lower():
        print(f"   CLOUDFLARE_API_KEY value: {cf_key[:10]}...{cf_key[-5:]}")
    
    print(f"   CLOUDFLARE_ACCOUNT_ID: {'✓ Configured' if cf_account and 'your-cloudflare' not in cf_account.lower() else '✗ Not configured (placeholder)'}")
    if cf_account and 'your-cloudflare' not in cf_account.lower():
        print(f"   CLOUDFLARE_ACCOUNT_ID value: {cf_account}")
    
    # Test generation
    print("\n2. Testing blueprint generation for 'Coca-Cola'...")
    print("   (This may take 30-60 seconds...)\n")
    
    result = await generate_blueprint_image("Coca-Cola", "")
    
    print("\n3. Result:")
    if result:
        print(f"   ✓ SUCCESS! Generated {len(result)} bytes")
        
        # Detect image type
        png_header = b'\x89PNG'
        jpeg_header = b'\xff\xd8'
        if result[:4] == png_header:
            img_type = "PNG"
        elif result[:2] == jpeg_header:
            img_type = "JPEG"
        else:
            img_type = "Unknown"
        print(f"   Image type: {img_type}")
        
        # Save to file
        output_file = "test_blueprint.png"
        with open(output_file, "wb") as f:
            f.write(result)
        print(f"   Saved to: {output_file}")
        print(f"\n   Open {output_file} to see the generated blueprint!")
    else:
        print("   ✗ FAILED - No image generated")
        print("   This means:")
        print("   - Cloudflare is not configured OR failed")
        print("   - HuggingFace is not configured OR credits depleted")
        print("   - Server will fall back to SVG blueprint")
    
    print("\n" + "=" * 60)
    print("Check the logs above for detailed error messages")
    print("=" * 60)

if __name__ == "__main__":
    # Load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file")
    except ImportError:
        print("python-dotenv not installed, using system environment")
    
    asyncio.run(test_blueprint())
