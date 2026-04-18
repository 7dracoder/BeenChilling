"""Inventory REST API — backed by Supabase Postgres."""
import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends, Cookie

from fridge_observer.models import FoodItem, FoodItemCreate, FoodItemUpdate
from fridge_observer.supabase_client import get_supabase
from fridge_observer.routers.auth_router import get_current_user
from fridge_observer.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/inventory", tags=["inventory"])


def _row_to_food_item(row: dict, threshold: int = 3) -> FoodItem:
    expiry_date = None
    if row.get("expiry_date"):
        try:
            expiry_date = date.fromisoformat(row["expiry_date"])
        except (ValueError, TypeError):
            pass

    added_at = row.get("added_at")
    if isinstance(added_at, str):
        try:
            added_at = datetime.fromisoformat(added_at.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            added_at = datetime.now()

    return FoodItem.with_threshold(
        {
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "quantity": row["quantity"],
            "expiry_date": expiry_date,
            "expiry_source": row.get("expiry_source", "estimated"),
            "added_at": added_at,
            "thumbnail": row.get("thumbnail"),
            "notes": row.get("notes"),
        },
        threshold,
    )


async def _broadcast_inventory_update(user_id: str) -> None:
    """Broadcast current inventory to all WebSocket clients."""
    try:
        from fridge_observer.ws_manager import manager
        sb = get_supabase()
        result = sb.table("food_items").select("*").eq("user_id", user_id).order("added_at", desc=True).execute()
        items = result.data or []
        await manager.broadcast_inventory_update(items)
    except Exception as exc:
        logger.warning("Failed to broadcast inventory update: %s", exc)


@router.get("", response_model=list[FoodItem])
async def get_inventory(
    category: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query("asc"),
    current_user: dict = Depends(get_current_user),
):
    settings = get_settings()
    sb = get_supabase()

    query = sb.table("food_items").select("*").eq("user_id", current_user["sub"])

    if category:
        query = query.eq("category", category)

    sort_column = sort_by if sort_by in ("expiry_date", "added_at", "name", "quantity") else "added_at"
    query = query.order(sort_column, desc=(sort_dir == "desc"))

    result = query.execute()
    rows = result.data or []

    items = []
    for row in rows:
        cat = row.get("category", "packaged_goods")
        threshold = settings.get_spoilage_threshold(cat)
        items.append(_row_to_food_item(row, threshold))

    return items


@router.post("", response_model=FoodItem, status_code=201)
async def create_inventory_item(
    item: FoodItemCreate,
    current_user: dict = Depends(get_current_user),
):
    settings = get_settings()
    sb = get_supabase()

    data = {
        "user_id": current_user["sub"],
        "name": item.name,
        "category": item.category.value,
        "quantity": item.quantity,
        "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
        "expiry_source": item.expiry_source,
        "notes": item.notes,
    }

    result = sb.table("food_items").insert(data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create item")

    row = result.data[0]

    # Log activity
    sb.table("activity_log").insert({
        "user_id": current_user["sub"],
        "item_id": row["id"],
        "item_name": item.name,
        "action": "added",
        "source": "manual",
    }).execute()

    await _broadcast_inventory_update(current_user["sub"])

    threshold = settings.get_spoilage_threshold(item.category.value)
    return _row_to_food_item(row, threshold)


@router.patch("/{item_id}", response_model=FoodItem)
async def update_inventory_item(
    item_id: int,
    patch: FoodItemUpdate,
    current_user: dict = Depends(get_current_user),
):
    settings = get_settings()
    sb = get_supabase()

    # Verify ownership
    existing = sb.table("food_items").select("*").eq("id", item_id).eq("user_id", current_user["sub"]).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Item not found")

    updates = {}
    if patch.name is not None: updates["name"] = patch.name
    if patch.quantity is not None: updates["quantity"] = patch.quantity
    if patch.expiry_date is not None: updates["expiry_date"] = patch.expiry_date.isoformat()
    if patch.expiry_source is not None: updates["expiry_source"] = patch.expiry_source
    if patch.notes is not None: updates["notes"] = patch.notes

    if updates:
        result = sb.table("food_items").update(updates).eq("id", item_id).eq("user_id", current_user["sub"]).execute()
        row = result.data[0] if result.data else existing.data
    else:
        row = existing.data

    sb.table("activity_log").insert({
        "user_id": current_user["sub"],
        "item_id": item_id,
        "item_name": row.get("name", ""),
        "action": "updated",
        "source": "manual",
    }).execute()

    await _broadcast_inventory_update(current_user["sub"])

    threshold = settings.get_spoilage_threshold(row.get("category", "packaged_goods"))
    return _row_to_food_item(row, threshold)


@router.delete("/{item_id}", status_code=204)
async def delete_inventory_item(
    item_id: int,
    current_user: dict = Depends(get_current_user),
):
    sb = get_supabase()

    existing = sb.table("food_items").select("id, name").eq("id", item_id).eq("user_id", current_user["sub"]).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Item not found")

    item_name = existing.data["name"]
    sb.table("food_items").delete().eq("id", item_id).eq("user_id", current_user["sub"]).execute()

    sb.table("activity_log").insert({
        "user_id": current_user["sub"],
        "item_id": item_id,
        "item_name": item_name,
        "action": "removed",
        "source": "manual",
    }).execute()

    await _broadcast_inventory_update(current_user["sub"])
