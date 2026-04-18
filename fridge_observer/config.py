from __future__ import annotations

"""Application configuration — loaded from Supabase settings table."""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    spoilage_threshold_fruits: int = 3
    spoilage_threshold_vegetables: int = 2
    spoilage_threshold_dairy: int = 3
    spoilage_threshold_beverages: int = 5
    spoilage_threshold_meat: int = 1
    spoilage_threshold_packaged_goods: int = 7
    temp_threshold_fridge: float = 8.0
    temp_threshold_freezer: float = -15.0
    shopping_list_enabled: bool = True
    echo_dot_enabled: bool = True
    gamification_enabled: bool = False
    shopping_list_webhook_url: str = ""

    def get_spoilage_threshold(self, category: str) -> int:
        return getattr(self, f"spoilage_threshold_{category}", 3)


# Global default settings (used when no user context)
_settings: Settings = Settings()


def get_settings() -> Settings:
    return _settings


async def reload() -> None:
    """Load default settings on startup."""
    global _settings
    _settings = Settings()


async def reload_for_user(user_id: str) -> Settings:
    """Load settings for a specific user from Supabase."""
    try:
        from fridge_observer.supabase_client import get_supabase
        sb = get_supabase()
        result = sb.table("settings").select("key, value").eq("user_id", user_id).execute()
        rows = result.data or []
        data = {row["key"]: row["value"] for row in rows}

        return Settings(
            spoilage_threshold_fruits=int(data.get("spoilage_threshold_fruits", "3")),
            spoilage_threshold_vegetables=int(data.get("spoilage_threshold_vegetables", "2")),
            spoilage_threshold_dairy=int(data.get("spoilage_threshold_dairy", "3")),
            spoilage_threshold_beverages=int(data.get("spoilage_threshold_beverages", "5")),
            spoilage_threshold_meat=int(data.get("spoilage_threshold_meat", "1")),
            spoilage_threshold_packaged_goods=int(data.get("spoilage_threshold_packaged_goods", "7")),
            temp_threshold_fridge=float(data.get("temp_threshold_fridge", "8.0")),
            temp_threshold_freezer=float(data.get("temp_threshold_freezer", "-15.0")),
            shopping_list_enabled=data.get("shopping_list_enabled", "true").lower() == "true",
            echo_dot_enabled=data.get("echo_dot_enabled", "true").lower() == "true",
            gamification_enabled=data.get("gamification_enabled", "false").lower() == "true",
            shopping_list_webhook_url=data.get("shopping_list_webhook_url", ""),
        )
    except Exception:
        return Settings()
