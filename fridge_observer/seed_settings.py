from __future__ import annotations

"""Seed default settings into the database if they don't already exist."""
from fridge_observer.db import get_db

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


async def seed_settings() -> None:
    """Insert default settings rows if they do not already exist."""
    async with get_db() as db:
        for key, value in DEFAULT_SETTINGS.items():
            await db.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
        await db.commit()
