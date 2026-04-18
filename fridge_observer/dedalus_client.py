"""Dedalus API client for product blueprint generation (ecoscan redesign)."""
import base64
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Dedalus API configuration
DEDALUS_API_KEY = os.environ.get("DEDALUS_API_KEY", "")
DEDALUS_BASE_URL = "https://api.dedalus.ai/v1"  # Update with actual endpoint


async def generate_product_blueprint(
    image_bytes: bytes,
    product_name: Optional[str] = None,
    mime_type: str = "image/jpeg"
) -> dict:
    """
    Send a product image to Dedalus ecoscan redesign API and get back
    an enhanced blueprint/visualization of the product.
    
    Args:
        image_bytes: Raw image bytes of the scanned product
        product_name: Optional name of the product for context
        mime_type: MIME type of the image (default: image/jpeg)
    
    Returns:
        {
            "blueprint_url": str,  # URL to the generated blueprint image
            "blueprint_data": str,  # Base64 encoded blueprint image
            "success": bool,
            "error": str (optional)
        }
    """
    if not DEDALUS_API_KEY:
        return {
            "success": False,
            "error": "Dedalus API key not configured",
            "blueprint_url": None,
            "blueprint_data": None
        }

    # Encode image to base64
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Prepare the request payload
    payload = {
        "image": image_b64,
        "mime_type": mime_type,
        "mode": "ecoscan_redesign",  # Use the ecoscan redesign feature
    }
    
    if product_name:
        payload["product_name"] = product_name

    headers = {
        "Authorization": f"Bearer {DEDALUS_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{DEDALUS_BASE_URL}/ecoscan/redesign",
                json=payload,
                headers=headers,
            )

            if response.status_code == 401:
                return {
                    "success": False,
                    "error": "Invalid Dedalus API key",
                    "blueprint_url": None,
                    "blueprint_data": None
                }

            if response.status_code == 429:
                return {
                    "success": False,
                    "error": "Rate limit exceeded. Please try again later.",
                    "blueprint_url": None,
                    "blueprint_data": None
                }

            response.raise_for_status()
            data = response.json()

            # Extract blueprint data from response
            # Adjust these fields based on actual Dedalus API response format
            return {
                "success": True,
                "blueprint_url": data.get("blueprint_url"),
                "blueprint_data": data.get("blueprint_image"),  # Base64 encoded
                "metadata": data.get("metadata", {}),
                "error": None
            }

    except httpx.HTTPStatusError as exc:
        logger.error("Dedalus API HTTP error: %s - %s", exc.response.status_code, exc.response.text)
        return {
            "success": False,
            "error": f"API error: {exc.response.status_code}",
            "blueprint_url": None,
            "blueprint_data": None
        }
    except Exception as exc:
        logger.error("Dedalus API request failed: %s", exc)
        return {
            "success": False,
            "error": str(exc),
            "blueprint_url": None,
            "blueprint_data": None
        }


async def save_blueprint_to_file(blueprint_data: str, output_path: str) -> bool:
    """
    Save a base64-encoded blueprint image to a file.
    
    Args:
        blueprint_data: Base64 encoded image data
        output_path: Path where to save the image file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        image_bytes = base64.b64decode(blueprint_data)
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        logger.info("Blueprint saved to %s", output_path)
        return True
    except Exception as exc:
        logger.error("Failed to save blueprint: %s", exc)
        return False
