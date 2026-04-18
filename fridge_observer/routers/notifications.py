from __future__ import annotations

"""Notifications REST API — backed by Supabase."""
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends

from fridge_observer.supabase_client import get_supabase
from fridge_observer.routers.auth_router import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/activity-log")
async def get_activity_log(current_user: dict = Depends(get_current_user)):
    sb = get_supabase()
    result = sb.table("activity_log").select("*").eq("user_id", current_user["sub"]).order("occurred_at", desc=True).limit(100).execute()
    return result.data or []


@router.get("/weekly-report")
async def get_weekly_report(current_user: dict = Depends(get_current_user)):
    sb = get_supabase()
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    two_weeks_ago = (now - timedelta(days=14)).isoformat()

    # Get data for 14 days
    result = sb.table("activity_log").select("action, occurred_at").eq("user_id", current_user["sub"]).gte("occurred_at", two_weeks_ago).execute()
    rows = result.data or []

    # Current week stats
    this_week = [r for r in rows if r["occurred_at"] >= week_ago]
    expired = sum(1 for r in this_week if r["action"] == "expired")
    consumed = sum(1 for r in this_week if r["action"] == "removed")
    added = sum(1 for r in this_week if r["action"] == "added")

    # Previous week stats
    prev_week = [r for r in rows if r["occurred_at"] < week_ago]
    prev_expired = sum(1 for r in prev_week if r["action"] == "expired")
    prev_consumed = sum(1 for r in prev_week if r["action"] == "consumed") # Wait, "removed" is consumed in this app
    prev_removed = sum(1 for r in prev_week if r["action"] == "removed") 
    prev_added = sum(1 for r in prev_week if r["action"] == "added")

    return {
        "this_week": {
            "expired": expired,
            "consumed": consumed,
            "added": added
        },
        "prev_week": {
            "expired": prev_expired,
            "consumed": prev_removed,
            "added": prev_added
        },
        "week_start": week_ago
    }


@router.get("/streak")
async def get_streak(current_user: dict = Depends(get_current_user)):
    sb = get_supabase()

    # Get last 12 weeks of activity
    twelve_weeks_ago = (datetime.now(timezone.utc) - timedelta(weeks=12)).isoformat()
    result = sb.table("activity_log").select("action, occurred_at").eq("user_id", current_user["sub"]).eq("action", "expired").gte("occurred_at", twelve_weeks_ago).execute()
    expired_rows = result.data or []

    # Calculate streak (consecutive weeks with no expired items)
    streak = 0
    now = datetime.now(timezone.utc)
    for week_offset in range(12):
        week_end = now - timedelta(weeks=week_offset)
        week_start = week_end - timedelta(weeks=1)
        had_expired = any(
            week_start.isoformat() <= r["occurred_at"] <= week_end.isoformat()
            for r in expired_rows
        )
        if had_expired:
            break
        streak += 1

    return {"streak": streak, "unit": "weeks"}
