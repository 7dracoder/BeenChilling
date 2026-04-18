"""Settings REST API — backed by Supabase."""
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from fridge_observer.supabase_client import get_supabase
from fridge_observer.routers.auth_router import get_current_user
import fridge_observer.config as config_module

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/settings", tags=["settings"])

DEFAULT_SETTINGS = {
    "spoilage_threshold_fruits": "3",
    "spoilage_threshold_vegetables": "2",
    "spoilage_threshold_dairy": "3",
    "spoilage_threshold_beverages": "5",
    "spoilage_threshold_meat": "1",
    "spoilage_threshold_packaged_goods": "7",
    "temp_threshold_fridge": "8.0",
    "temp_threshold_freezer": "-15.0",
    "shopping_list_enabled": "true",
    "echo_dot_enabled": "true",
    "gamification_enabled": "false",
    "shopping_list_webhook_url": "",
}


class SettingsPatch(BaseModel):
    spoilage_threshold_fruits: Optional[int] = None
    spoilage_threshold_vegetables: Optional[int] = None
    spoilage_threshold_dairy: Optional[int] = None
    spoilage_threshold_beverages: Optional[int] = None
    spoilage_threshold_meat: Optional[int] = None
    spoilage_threshold_packaged_goods: Optional[int] = None
    temp_threshold_fridge: Optional[float] = None
    temp_threshold_freezer: Optional[float] = None
    shopping_list_enabled: Optional[bool] = None
    echo_dot_enabled: Optional[bool] = None
    gamification_enabled: Optional[bool] = None
    shopping_list_webhook_url: Optional[str] = None


@router.get("")
async def get_settings_endpoint(current_user: dict = Depends(get_current_user)):
    sb = get_supabase()
    result = sb.table("settings").select("key, value").eq("user_id", current_user["sub"]).execute()
    rows = result.data or []
    data = {**DEFAULT_SETTINGS}
    for row in rows:
        data[row["key"]] = row["value"]
    return data


@router.patch("")
async def patch_settings(body: SettingsPatch, current_user: dict = Depends(get_current_user)):
    sb = get_supabase()
    updates = body.model_dump(exclude_none=True)

    for key, value in updates.items():
        sb.table("settings").upsert({
            "user_id": current_user["sub"],
            "key": key,
            "value": str(value).lower() if isinstance(value, bool) else str(value),
        }).execute()

    await config_module.reload_for_user(current_user["sub"])
    return {"status": "saved"}
