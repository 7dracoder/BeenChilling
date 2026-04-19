#!/usr/bin/env python3
"""Fix user account - confirm email and/or reset password."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fridge_observer.supabase_client import get_supabase

def list_all_users():
    """List all users."""
    sb = get_supabase()
    users = sb.auth.admin.list_users()
    
    print(f"\nTotal users: {len(users)}\n")
    
    for i, user in enumerate(users, 1):
        email = user.email or "no-email"
        confirmed = "✓" if user.email_confirmed_at else "✗"
        display_name = (user.user_metadata or {}).get("display_name", "")
        
        print(f"{i}. {email} {confirmed}")
        if display_name:
            print(f"   Name: {display_name}")
    
    return users

def confirm_and_reset(email: str, new_password: str = None):
    """Confirm email and optionally reset password."""
    try:
        sb = get_supabase()
        
        # Find user
        users = sb.auth.admin.list_users()
        user = next((u for u in users if u.email.lower() == email.lower()), None)
        
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        print(f"\n✓ Found user: {user.email}")
        print(f"  ID: {user.id}")
        print(f"  Name: {(user.user_metadata or {}).get('display_name', 'N/A')}")
        print(f"  Email confirmed: {user.email_confirmed_at is not None}")
        
        # Confirm email if not confirmed
        if not user.email_confirmed_at:
            print("\n→ Confirming email...")
            sb.auth.admin.update_user_by_id(user.id, {"email_confirm": True})
            print("✓ Email confirmed")
        else:
            print("✓ Email already confirmed")
        
        # Reset password if provided
        if new_password:
            print(f"\n→ Setting new password...")
            sb.auth.admin.update_user_by_id(user.id, {"password": new_password})
            print("✓ Password updated")
        
        print(f"\n✓ Account ready! You can now login with:")
        print(f"  Email: {email}")
        if new_password:
            print(f"  Password: {new_password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python fix_user_account.py <email> [new_password]")
        print("\nExamples:")
        print("  python fix_user_account.py user@example.com")
        print("  python fix_user_account.py user@example.com newpassword123")
        print("\nThis will:")
        print("  1. Confirm the user's email (if not confirmed)")
        print("  2. Reset password (if provided)")
        
        list_all_users()
        sys.exit(1)
    
    email = sys.argv[1].strip()
    new_password = sys.argv[2].strip() if len(sys.argv) > 2 else None
    
    success = confirm_and_reset(email, new_password)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
