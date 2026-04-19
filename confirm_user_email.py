#!/usr/bin/env python3
"""Manually confirm a user's email."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fridge_observer.supabase_client import get_supabase

def confirm_email(email: str):
    """Manually confirm a user's email."""
    try:
        sb = get_supabase()
        
        # Find user
        users = sb.auth.admin.list_users()
        user = next((u for u in users if u.email == email), None)
        
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        print(f"Found user: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Name: {(user.user_metadata or {}).get('display_name', 'N/A')}")
        print(f"  Currently confirmed: {user.email_confirmed_at is not None}")
        
        if user.email_confirmed_at:
            print("✓ Email already confirmed!")
            return True
        
        # Confirm the email
        print("\nConfirming email...")
        sb.auth.admin.update_user_by_id(user.id, {"email_confirm": True})
        
        # Verify it worked
        users = sb.auth.admin.list_users()
        user = next((u for u in users if u.email == email), None)
        
        if user and user.email_confirmed_at:
            print("✓ Email confirmed successfully!")
            print(f"  Confirmed at: {user.email_confirmed_at}")
            print(f"\n✓ User can now login with their password")
            return True
        else:
            print("⚠ Confirmation may have failed - please check manually")
            return False
        
    except Exception as e:
        print(f"❌ Failed to confirm email: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python confirm_user_email.py <email>")
        print("\nAvailable unconfirmed users:")
        try:
            sb = get_supabase()
            users = sb.auth.admin.list_users()
            for u in users:
                if not u.email_confirmed_at:
                    print(f"  - {u.email}")
        except:
            pass
        sys.exit(1)
    
    email = sys.argv[1].strip().lower()
    success = confirm_email(email)
    sys.exit(0 if success else 1)
