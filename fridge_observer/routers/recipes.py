from __future__ import annotations

"""Recipes REST API — backed by Supabase."""
import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends

from fridge_observer.models import Recipe, RecipeIngredient, ScoredRecipe
from fridge_observer.supabase_client import get_supabase
from fridge_observer.routers.auth_router import get_current_user
from fridge_observer.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _compute_urgency_score(ingredients, inventory, threshold):
    today = date.today()
    score = 0.0
    matching = []
    inv_by_name = {item["name"].lower(): item for item in inventory}

    for ing in ingredients:
        if ing.get("is_pantry_staple"):
            continue
        inv_item = inv_by_name.get(ing["name"].lower())
        if not inv_item:
            continue
        expiry_str = inv_item.get("expiry_date")
        if not expiry_str:
            continue
        try:
            expiry = date.fromisoformat(expiry_str[:10])
        except (ValueError, TypeError):
            continue
        days = (expiry - today).days
        if days <= 0:
            score += 1.0
            matching.append(ing["name"])
        elif days <= threshold:
            score += (threshold - days) / threshold
            matching.append(ing["name"])

    return score, matching


@router.get("", response_model=list[ScoredRecipe])
async def get_recipes(
    dietary: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    max_prep_minutes: Optional[int] = Query(None),
    favorites_only: bool = Query(False),
    current_user: dict = Depends(get_current_user),
):
    settings = get_settings()
    threshold = settings.spoilage_threshold_fruits
    sb = get_supabase()

    # Get inventory
    inv_result = sb.table("food_items").select("name, category, expiry_date").eq("user_id", current_user["sub"]).execute()
    inventory = inv_result.data or []

    # Get favorites
    fav_result = sb.table("recipe_favorites").select("recipe_id").eq("user_id", current_user["sub"]).execute()
    fav_ids = {r["recipe_id"] for r in (fav_result.data or [])}

    # Build recipe query
    query = sb.table("recipes").select("*, recipe_ingredients(*)")
    if cuisine:
        query = query.ilike("cuisine", cuisine)
    if max_prep_minutes:
        query = query.lte("prep_minutes", max_prep_minutes)
    if favorites_only:
        if not fav_ids:
            return []
        query = query.in_("id", list(fav_ids))

    result = query.execute()
    recipes_data = result.data or []

    scored = []
    for r in recipes_data:
        tags = r.get("dietary_tags") or []
        if isinstance(tags, str):
            import json
            try: tags = json.loads(tags)
            except: tags = []

        if dietary and dietary.lower() not in [t.lower() for t in tags]:
            continue

        ingredients = r.get("recipe_ingredients") or []
        score, matching = _compute_urgency_score(ingredients, inventory, threshold)

        recipe_obj = Recipe(
            id=r["id"],
            name=r["name"],
            description=r.get("description"),
            cuisine=r.get("cuisine"),
            dietary_tags=tags,
            prep_minutes=r.get("prep_minutes"),
            instructions=r["instructions"],
            image_url=r.get("image_url"),
            ingredients=[
                RecipeIngredient(
                    id=i["id"],
                    recipe_id=i["recipe_id"],
                    name=i["name"],
                    category=i.get("category"),
                    is_pantry_staple=bool(i.get("is_pantry_staple", False)),
                )
                for i in ingredients
            ],
            is_favorite=r["id"] in fav_ids,
        )
        scored.append(ScoredRecipe(recipe=recipe_obj, urgency_score=score, matching_expiring_items=matching))

    scored.sort(key=lambda x: x.urgency_score, reverse=True)
    return scored


@router.post("/{recipe_id}/favorite", status_code=201)
async def add_favorite(recipe_id: int, current_user: dict = Depends(get_current_user)):
    sb = get_supabase()
    sb.table("recipe_favorites").upsert({"user_id": current_user["sub"], "recipe_id": recipe_id}).execute()
    return {"status": "favorited", "recipe_id": recipe_id}


@router.delete("/{recipe_id}/favorite", status_code=204)
async def remove_favorite(recipe_id: int, current_user: dict = Depends(get_current_user)):
    sb = get_supabase()
    sb.table("recipe_favorites").delete().eq("user_id", current_user["sub"]).eq("recipe_id", recipe_id).execute()


@router.post("/{recipe_id}/made-this", status_code=200)
async def made_this(recipe_id: int, current_user: dict = Depends(get_current_user)):
    sb = get_supabase()

    recipe = sb.table("recipes").select("id, name").eq("id", recipe_id).single().execute()
    if not recipe.data:
        raise HTTPException(status_code=404, detail="Recipe not found")

    ingredients = sb.table("recipe_ingredients").select("*").eq("recipe_id", recipe_id).execute()
    removed = []

    for ing in (ingredients.data or []):
        if ing.get("is_pantry_staple"):
            continue
        item = sb.table("food_items").select("id, name").eq("user_id", current_user["sub"]).ilike("name", ing["name"]).limit(1).execute()
        if item.data:
            item_row = item.data[0]
            sb.table("food_items").delete().eq("id", item_row["id"]).execute()
            sb.table("activity_log").insert({
                "user_id": current_user["sub"],
                "item_id": item_row["id"],
                "item_name": item_row["name"],
                "action": "removed",
                "source": "manual",
            }).execute()
            removed.append(item_row["name"])

    # Broadcast update
    try:
        from fridge_observer.ws_manager import manager
        inv = sb.table("food_items").select("*").eq("user_id", current_user["sub"]).execute()
        await manager.broadcast_inventory_update(inv.data or [])
    except Exception as exc:
        logger.warning("Broadcast failed: %s", exc)

    return {"status": "ok", "removed_items": removed}


@router.get("/{recipe_id}/detail")
async def get_recipe_detail(recipe_id: int, current_user: dict = Depends(get_current_user)):
    """
    Get full recipe detail. Uses K2-Think to generate complete structured recipe
    with quantities, measurements, and step-by-step instructions.
    """
    sb = get_supabase()

    recipe = sb.table("recipes").select("*, recipe_ingredients(*)").eq("id", recipe_id).single().execute()
    if not recipe.data:
        raise HTTPException(status_code=404, detail="Recipe not found")

    r = recipe.data
    tags = r.get("dietary_tags") or []
    if isinstance(tags, str):
        import json as _json
        try: tags = _json.loads(tags)
        except: tags = []

    ingredients = r.get("recipe_ingredients") or []

    # Check which ingredients are expiring in user's fridge
    inv = sb.table("food_items").select("name, expiry_date").eq("user_id", current_user["sub"]).execute()
    inv_map = {}
    today = date.today()
    for i in (inv.data or []):
        days = None
        if i.get("expiry_date"):
            try:
                days = (date.fromisoformat(i["expiry_date"][:10]) - today).days
            except Exception:
                pass
        status = "ok"
        if days is not None:
            if days <= 0:
                status = "expired"
            elif days <= 3:
                status = "warning"
        inv_map[i["name"].lower()] = {"expiry_status": status}

    # Mark ingredients with expiry info
    enriched_ingredients = []
    for ing in ingredients:
        inv_item = inv_map.get(ing["name"].lower())
        enriched_ingredients.append({
            "name": ing["name"],
            "category": ing.get("category"),
            "is_pantry_staple": bool(ing.get("is_pantry_staple", False)),
            "in_fridge": inv_item is not None,
            "expiry_status": inv_item.get("expiry_status") if inv_item else None,
        })

    # Use K2 to generate the full structured recipe
    full_recipe = await _generate_full_recipe_with_k2(
        name=r["name"],
        description=r.get("description", ""),
        cuisine=r.get("cuisine", ""),
        prep_minutes=r.get("prep_minutes"),
        ingredients=enriched_ingredients,
        raw_instructions=r.get("instructions", ""),
    )

    return {
        "id": r["id"],
        "name": r["name"],
        "description": r.get("description"),
        "cuisine": r.get("cuisine"),
        "dietary_tags": tags,
        "prep_minutes": r.get("prep_minutes"),
        "servings": full_recipe.get("servings", 2),
        "ingredients": enriched_ingredients,
        "quantities": full_recipe.get("quantities", {}),
        "steps": full_recipe.get("steps", []),
        "tips": full_recipe.get("tips", ""),
        "image_url": r.get("image_url"),
    }


async def _generate_full_recipe_with_k2(
    name: str,
    description: str,
    cuisine: str,
    prep_minutes: int | None,
    ingredients: list[dict],
    raw_instructions: str,
) -> dict:
    """
    Use K2-Think to generate a complete structured recipe with quantities and steps.
    Returns: {servings, quantities: {name: qty}, steps: [str], tips: str}
    """
    import json as _json
    from fridge_observer.ai_client import k2_chat, ANSWER_SEP

    ing_names = [i["name"] for i in ingredients]
    prep_str = f"{prep_minutes} minutes" if prep_minutes else "quick"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional chef. Generate complete, accurate recipe details. "
                "Always respond with ONLY valid JSON after the separator — no extra text.\n\n"
                f"FORMAT: {ANSWER_SEP}\n{{...}}"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Recipe: {name}\n"
                f"Cuisine: {cuisine or 'International'}\n"
                f"Description: {description or name}\n"
                f"Prep time: {prep_str}\n"
                f"Ingredients available: {', '.join(ing_names)}\n\n"
                "Generate a complete recipe JSON with this exact structure:\n"
                "{\n"
                '  "servings": 2,\n'
                '  "quantities": {\n'
                '    "ingredient name": "amount + unit (e.g. 200g, 2 cups, 3 tbsp)"\n'
                "  },\n"
                '  "steps": [\n'
                '    "Step description with specific temperatures, times, and techniques",\n'
                '    "Next step..."\n'
                "  ],\n"
                '  "tips": "One practical cooking tip for this recipe"\n'
                "}\n\n"
                "Make quantities realistic for 2 servings. Steps should be clear and specific."
            ),
        },
    ]

    try:
        response = await k2_chat(messages, stream=False)

        # Extract JSON after separator
        if ANSWER_SEP in response:
            json_str = response.rsplit(ANSWER_SEP, 1)[1].strip()
        else:
            # Try to find JSON block
            import re
            match = re.search(r'\{[\s\S]*\}', response)
            json_str = match.group(0) if match else "{}"

        # Clean markdown fences
        if "```" in json_str:
            parts = json_str.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    json_str = part
                    break

        result = _json.loads(json_str.strip())

        # Validate structure
        if not isinstance(result.get("steps"), list):
            result["steps"] = _parse_instructions(raw_instructions)
        if not isinstance(result.get("quantities"), dict):
            result["quantities"] = {}
        if not result.get("servings"):
            result["servings"] = 2

        return result

    except Exception as exc:
        logger.warning("K2 recipe generation failed: %s", exc)
        # Fallback to parsed instructions
        return {
            "servings": 2,
            "quantities": {},
            "steps": _parse_instructions(raw_instructions),
            "tips": "",
        }


def _parse_instructions(raw: str) -> list[str]:
    """Parse numbered instructions into a list of steps."""
    import re
    steps = re.split(r'\d+\.\s+', raw)
    steps = [s.strip() for s in steps if s.strip()]
    if not steps and raw:
        steps = [s.strip() for s in raw.split('.') if s.strip()]
    return steps or [raw]
