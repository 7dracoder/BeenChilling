#!/usr/bin/env python3
"""List all users and their email confirmation status."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fridge_observer.supabase_client import get_supabase

def list_users():
    """List all users."""
    try:
        sb = get_supabase()
        users = sb.auth.admin.list_users()
        
        print(f"Total users: {len(users)}\n")
        
        for i, user in enumerate(users, 1):
            email = user.email or "no-email"
            masked = email[:3] + "***@" + email.split("@")[1] if "@" in email else "***"
            confirmed = "✓ Confirmed" if user.email_confirmed_at else "✗ Not confirmed"
            
            print(f"{i}. {masked}")
            print(f"   ID: {user.id}")
            print(f"   Status: {confirmed}")
            print(f"   Created: {user.created_at}")
            
            # Check if they have display name
            display_name = (user.user_metadata or {}).get("display_name", "")
            if display_name:
                print(f"   Name: {display_name}")
            
            print()
        
        # Count confirmed vs unconfirmed
        confirmed_count = sum(1 for u in users if u.email_confirmed_at)
        unconfirmed_count = len(users) - confirmed_count
        
        print(f"Summary:")
        print(f"  Confirmed: {confirmed_count}")
        print(f"  Unconfirmed: {unconfirmed_count}")
        
        if unconfirmed_count > 0:
            print(f"\n⚠ {unconfirmed_count} user(s) need email verification")
            print("  They won't be able to login until they verify their email with OTP")
        
    except Exception as e:
        print(f"❌ Failed to list users: {e}")
        return False

if __name__ == "__main__":
    list_users()
