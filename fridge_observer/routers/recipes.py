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
