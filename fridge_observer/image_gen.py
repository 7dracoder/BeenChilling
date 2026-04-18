"""
Image fetching — uses Unsplash for free food photos (no API key needed).
Falls back to HF FLUX when credits are available.
Blueprint generation uses Replicate AI, or HF FLUX.
"""
import asyncio
import base64
import io
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

HF_TOKEN = os.environ.get("HF_TOKEN", "")
DEDALUS_API_KEY = os.environ.get("DEDALUS_API_KEY", "")
CLOUDFLARE_API_KEY = os.environ.get("CLOUDFLARE_API_KEY", "")
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
FAL_KEY = os.environ.get("FAL_KEY", "")
_hf_credits_depleted = False

HF_MODELS = [
    "black-forest-labs/FLUX.1-schnell",
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-xl-base-1.0",
]


# ── LoremFlickr (free, keyword-based photos) ─────────────────

async def _fetch_photo(query: str, width: int = 512, height: int = 512) -> Optional[bytes]:
    """
    Fetch a free keyword-based photo from LoremFlickr.
    Returns real photos matching the keywords — completely free, no API key.
    """
    # LoremFlickr format: /width/height/keyword1,keyword2
    clean = query.replace(" ", ",").replace("'", "").lower()
    # Keep only the most relevant keywords (max 3)
    keywords = [k.strip() for k in clean.split(",") if k.strip() and len(k.strip()) > 2][:3]
    keyword_str = ",".join(keywords)
    url = f"https://loremflickr.com/{width}/{height}/{keyword_str}"

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            r = await client.get(url)
            if r.status_code == 200 and len(r.content) > 5000:
                logger.info("LoremFlickr: %d bytes for '%s'", len(r.content), keyword_str)
                return r.content
    except Exception as exc:
        logger.warning("LoremFlickr failed for '%s': %s", keyword_str, exc)
    return None


# ── Unsplash (free, high-quality food photos) ────────────────

async def _fetch_unsplash_photo(query: str, width: int = 800, height: int = 600) -> Optional[bytes]:
    """
    Fetch a high-quality food photo from Unsplash.
    Uses Unsplash Source API - completely free, no API key needed.
    Much more accurate than LoremFlickr for food images.
    """
    # Unsplash Source format: /featured/?food,query
    # Add 'food' to every query to ensure we get food photos
    clean_query = query.replace(" ", ",").lower()
    url = f"https://source.unsplash.com/featured/{width}x{height}/?food,{clean_query}"
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            r = await client.get(url)
            if r.status_code == 200 and len(r.content) > 5000:
                logger.info("Unsplash: %d bytes for 'food,%s'", len(r.content), clean_query)
                return r.content
    except Exception as exc:
        logger.warning("Unsplash failed for '%s': %s", clean_query, exc)
    return None


# ── HF FLUX (when credits available) ─────────────────────────

def _hf_generate_sync(prompt: str, width: int, height: int, steps: int) -> Optional[bytes]:
    global _hf_credits_depleted
    if not HF_TOKEN or _hf_credits_depleted:
        return None
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=HF_TOKEN)
    except Exception:
        return None

    for model in HF_MODELS:
        try:
            image = client.text_to_image(prompt, model=model, width=width, height=height, num_inference_steps=steps)
            buf = io.BytesIO()
            image.save(buf, format="JPEG", quality=85)
            buf.seek(0)
            logger.info("HF image: %d bytes", buf.getbuffer().nbytes)
            return buf.read()
        except Exception as exc:
            err = str(exc).lower()
            if "402" in err or "payment" in err or "credits" in err or "depleted" in err:
                logger.warning("HF credits depleted — using Unsplash")
                _hf_credits_depleted = True
                return None
            elif "loading" in err or "503" in err:
                continue
            else:
                logger.warning("HF %s failed: %s", model, exc)
                continue
    return None


async def _hf_generate(prompt: str, width: int, height: int, steps: int = 4) -> Optional[bytes]:
    if not HF_TOKEN or _hf_credits_depleted:
        return None
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _hf_generate_sync, prompt, width, height, steps)


# ── Public API ────────────────────────────────────────────────

async def generate_recipe_image(recipe_name: str, cuisine: str = "") -> Optional[bytes]:
    """Get a food photo for a recipe — uses Unsplash for accurate food images."""
    # Map recipe names to better search terms
    name_lower = recipe_name.lower()
    
    # Build specific query for Unsplash
    if "omelette" in name_lower or "omelet" in name_lower:
        query = "omelette breakfast eggs"
    elif "stir" in name_lower and "fry" in name_lower:
        query = "stir fry wok asian"
    elif "curry" in name_lower:
        query = "curry indian spices"
    elif "salmon" in name_lower:
        query = "salmon fish seafood"
    elif "pasta" in name_lower:
        query = "pasta italian"
    elif "pancake" in name_lower:
        query = "pancakes breakfast"
    elif "salad" in name_lower:
        query = "salad fresh vegetables"
    elif "soup" in name_lower:
        query = "soup bowl"
    elif "taco" in name_lower or "burrito" in name_lower:
        query = "tacos mexican"
    elif "pizza" in name_lower:
        query = "pizza italian"
    elif "chicken" in name_lower:
        query = "chicken dish"
    elif "beef" in name_lower or "steak" in name_lower:
        query = "beef steak"
    elif "burger" in name_lower:
        query = "burger"
    elif "sandwich" in name_lower:
        query = "sandwich"
    elif "rice" in name_lower:
        query = "rice dish"
    elif "noodle" in name_lower:
        query = "noodles"
    elif "sushi" in name_lower:
        query = "sushi japanese"
    elif "dessert" in name_lower or "cake" in name_lower:
        query = "dessert cake"
    else:
        # Generic food photo with cuisine hint
        query = f"{recipe_name.lower()}"
        if cuisine:
            query = f"{cuisine.lower()} {query}"
    
    # Try Unsplash first (more accurate)
    result = await _fetch_unsplash_photo(query, 800, 600)
    if result:
        return result
    
    # Fallback to LoremFlickr if Unsplash fails
    return await _fetch_photo(query, 512, 512)


async def generate_food_item_image(item_name: str, category: str = "") -> Optional[bytes]:
    """Get a food item photo — uses Unsplash for accurate food images."""
    name_lower = item_name.lower()
    
    # Map common items to better search terms for Unsplash
    item_map = {
        "milk": "milk glass dairy",
        "eggs": "eggs fresh",
        "chicken": "raw chicken meat",
        "salmon": "salmon fish",
        "spinach": "spinach leaves",
        "mushrooms": "mushrooms fresh",
        "tomatoes": "tomatoes red",
        "cheese": "cheese dairy",
        "butter": "butter dairy",
        "lemon": "lemon citrus",
        "pasta": "pasta dry",
        "rice": "rice grain",
        "broccoli": "broccoli vegetable",
        "carrots": "carrots orange",
        "potatoes": "potatoes",
        "onion": "onion vegetable",
        "garlic": "garlic",
        "zucchini": "zucchini",
        "asparagus": "asparagus",
        "bread": "bread loaf",
        "apple": "apple fruit",
        "banana": "banana fruit",
        "orange": "orange citrus",
        "strawberry": "strawberries",
        "yogurt": "yogurt dairy",
    }
    
    query = item_map.get(name_lower)
    if not query:
        # Build from name and category
        cat_map = {
            "fruits": "fruit",
            "vegetables": "vegetable",
            "dairy": "dairy",
            "meat": "meat",
            "beverages": "drink"
        }
        cat_hint = cat_map.get(category, "food")
        query = f"{name_lower} {cat_hint}"
    
    # Try Unsplash first (more accurate)
    result = await _fetch_unsplash_photo(query, 400, 400)
    if result:
        return result
    
    # Fallback to LoremFlickr if Unsplash fails
    return await _fetch_photo(query, 256, 256)


async def generate_blueprint_image(product_name: str, redesign_spec: str = "") -> Optional[bytes]:
    """
    Generate a sustainable product blueprint using AI services.
    Priority: FAL.ai → Replicate → HF FLUX → Return None (use SVG)
    {product_name.upper()}
    """
    # Build a comprehensive technical blueprint prompt
    prompt = f"A high-resolution, multi-panel technical blueprint illustration on an aged, blue textured grid-paper background with glowing cyan and green vector lines, detailing a comprehensive and sustainable product lifecycle schema for a {product_name.upper()}. The composition is structured as an interconnected circular economy infographic, with a prominent central diagram showing the {product_name.upper()} contained within a continuous 'CLOSED-LOOP CYCLE' flow arrow. Multiple dense callout labels with detailed, plausible technical specifications point directly to features like 'WEIGHT-OPTIMIZED LOGISTICS DESIGN,' 'NON-TOXIC SOLDER & ADHESIVES,' 'TRACEABLE MATERIAL QR-CODE TRACKER,' and 'MODULAR ASSEMBLY FOR REPAIR.' Encasing the central diagram are dedicated, labeled panels with icons: a top-right panel for 'RESPONSIBLE MATERIAL SOURCING' (e.g., regenerative agriculture, recycled polymers), a middle-right panel for 'CLEAN PRODUCTION & ENERGY STEWARDSHIP' (solar powered facilities, closed-loop water recycling), a bottom-right panel for 'REGIONAL LOGISTICS & REVERSE DISTRIBUTION' (electric fleet map), and a far-right panel for 'CONSUMER ENGAGEMENT & TAKE-BACK PROGRAM' (return kiosks, smartphone impact app). The entire blueprint has a professional schema look with dense data visualization and a prominent title box with a red 'CONFIDENTIAL' stamp."
    
    logger.info(f"Generating blueprint for '{product_name}' with detailed prompt")
    
    # Try FAL.ai first (FREE tier available!)
    if FAL_KEY and "your-fal" not in FAL_KEY.lower():
        try:
            logger.info("Attempting FAL.ai FLUX blueprint generation...")
            
            headers = {
                "Authorization": f"Key {FAL_KEY}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "prompt": prompt,
                "image_size": "landscape_16_9",
                "num_inference_steps": 4,
                "num_images": 1
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "https://fal.run/fal-ai/flux/schnell",
                    json=payload,
                    headers=headers,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    images = data.get("images", [])
                    if images and len(images) > 0:
                        image_url = images[0].get("url")
                        if image_url:
                            # Download the image
                            img_response = await client.get(image_url)
                            if img_response.status_code == 200:
                                logger.info("✓ FAL.ai blueprint generated: %d bytes", len(img_response.content))
                                return img_response.content
                else:
                    logger.warning("FAL.ai API error: %d - %s", response.status_code, response.text[:200])
        
        except Exception as exc:
            logger.warning("FAL.ai API failed for '%s': %s", product_name, exc)
    else:
        if not FAL_KEY:
            logger.info("FAL.ai not configured - skipping")
        else:
            logger.info("FAL.ai key is placeholder - skipping")
    
    # Try Replicate API (most reliable, but requires payment)
    if REPLICATE_API_TOKEN and "your-replicate" not in REPLICATE_API_TOKEN.lower():
        try:
            logger.info("Attempting Replicate FLUX 1.1 Pro blueprint generation (best prompt adherence)...")
            
            headers = {
                "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
                "Content-Type": "application/json",
            }
            
            # Use FLUX 1.1 Pro - best for prompt adherence and detailed technical images
            payload = {
                "version": "609793a667ed94b210242837d3c3c9fc9a64ae93685f15d75002ba0ed9a97f2b",
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                    "output_format": "jpg",
                    "output_quality": 90,
                    "safety_tolerance": 2,
                    "prompt_upsampling": True  # Enhances the prompt for better results
                }
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Start prediction
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    json=payload,
                    headers=headers,
                )
                
                if response.status_code == 201:
                    data = response.json()
                    prediction_url = data.get("urls", {}).get("get")
                    
                    # Poll for result
                    for _ in range(60):  # Wait up to 60 seconds
                        await asyncio.sleep(1)
                        result_response = await client.get(prediction_url, headers=headers)
                        result_data = result_response.json()
                        
                        if result_data.get("status") == "succeeded":
                            output = result_data.get("output")
                            # Output can be a list or a single URL
                            output_url = output[0] if isinstance(output, list) else output
                            if output_url:
                                # Download the image
                                img_response = await client.get(output_url)
                                if img_response.status_code == 200:
                                    logger.info("✓ Replicate blueprint generated: %d bytes", len(img_response.content))
                                    return img_response.content
                        elif result_data.get("status") == "failed":
                            logger.warning("Replicate generation failed: %s", result_data.get("error"))
                            break
                else:
                    logger.warning("Replicate API error: %d - %s", response.status_code, response.text[:200])
        
        except Exception as exc:
            logger.warning("Replicate API failed for '%s': %s", product_name, exc)
    else:
        if not REPLICATE_API_TOKEN:
            logger.info("Replicate not configured - skipping")
        else:
            logger.info("Replicate token is placeholder - skipping")
    
    # Try HF FLUX (you have a token configured)
    if HF_TOKEN and not _hf_credits_depleted:
        logger.info("Attempting HuggingFace FLUX blueprint generation...")
        result = await _hf_generate(prompt, 1536, 1024, steps=8)
        if result:
            logger.info("✓ HuggingFace blueprint generated: %d bytes", len(result))
            return result
        else:
            logger.warning("HuggingFace generation failed or credits depleted")
    else:
        if not HF_TOKEN:
            logger.info("HuggingFace token not configured - skipping")
        else:
            logger.info("HuggingFace credits depleted - skipping")
    
    # Try Cloudflare Workers AI (if configured properly)
    if CLOUDFLARE_API_KEY and CLOUDFLARE_ACCOUNT_ID:
        # Check if keys are not placeholder values
        if "your-cloudflare" not in CLOUDFLARE_API_KEY.lower() and "your-cloudflare" not in CLOUDFLARE_ACCOUNT_ID.lower() and not CLOUDFLARE_API_KEY.startswith("cfut_"):
            try:
                logger.info("Attempting Cloudflare Workers AI blueprint generation...")
                
                headers = {
                    "Authorization": f"Bearer {CLOUDFLARE_API_KEY}",
                    "Content-Type": "application/json",
                }
                
                payload = {"prompt": prompt}
                
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(
                        f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell",
                        json=payload,
                        headers=headers,
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Cloudflare returns base64 image in result
                        if "result" in data and "image" in data["result"]:
                            image_b64 = data["result"]["image"]
                            image_bytes = base64.b64decode(image_b64)
                            logger.info("✓ Cloudflare blueprint generated: %d bytes for '%s'", len(image_bytes), product_name)
                            return image_bytes
                    
                    else:
                        logger.warning("Cloudflare API error: %d - %s", response.status_code, response.text[:200])
            
            except Exception as exc:
                logger.warning("Cloudflare API failed for '%s': %s", product_name, exc)
        else:
            if CLOUDFLARE_API_KEY.startswith("cfut_"):
                logger.info("Cloudflare token is User Token (cfut_), not API Token - skipping")
            else:
                logger.info("Cloudflare keys are placeholders - skipping")
    else:
        logger.info("Cloudflare not configured - skipping")

    # Return None to use SVG instead of random photos
    logger.info("No AI image service available - will use SVG blueprint fallback")
    return None


async def generate_image(prompt: str, width: int = 512, height: int = 512, num_inference_steps: int = 4) -> Optional[bytes]:
    """Generic image generation."""
    result = await _hf_generate(prompt, width, height, num_inference_steps)
    if result:
        return result
    words = [w for w in prompt.split() if len(w) > 4 and w.isalpha()][:5]
    return await _fetch_photo(",".join(words), width, height)


def image_to_data_url(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"
