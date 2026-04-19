#!/usr/bin/env python3
"""Check user's inventory and matching recipes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fridge_observer.supabase_client import get_supabase

def check_user_inventory(user_id: str):
    """Check what's in the user's fridge and what recipes match."""
    sb = get_supabase()
    
    # Get user's inventory
    print(f"Checking inventory for user: {user_id}\n")
    inv = sb.table("food_items").select("*").eq("user_id", user_id).execute()
    
    print(f"Items in fridge: {len(inv.data)}")
    for item in inv.data:
        print(f"  - {item['name']} (category: {item.get('category', 'N/A')})")
    
    if not inv.data:
        print("\n❌ Fridge is empty! Add items to see recipes.")
        return
    
    print("\n" + "="*60)
    print("Checking recipes...")
    print("="*60 + "\n")
    
    # Get all recipes
    recipes = sb.table("recipes").select("*, recipe_ingredients(*)").execute()
    
    print(f"Total recipes in database: {len(recipes.data)}\n")
    
    # Check which recipes can be made
    item_names = [item['name'].lower() for item in inv.data]
    
    for recipe in recipes.data:
        ingredients = recipe.get("recipe_ingredients", [])
        non_pantry = [i for i in ingredients if not i.get("is_pantry_staple")]
        
        # Check if any ingredient matches
        matching = []
        for ing in non_pantry:
            if ing['name'].lower() in item_names:
                matching.append(ing['name'])
        
        if matching or len(non_pantry) == 0:
            print(f"✓ {recipe['name']}")
            print(f"  Non-pantry ingredients: {len(non_pantry)}")
            if non_pantry:
                print(f"  Needs: {', '.join([i['name'] for i in non_pantry])}")
            if matching:
                print(f"  ✓ You have: {', '.join(matching)}")
            print()

if __name__ == "__main__":
    # Use the user ID from ts3915789@gmail.com
    user_id = "3d16c0db-5f68-4b44-b579-0111e65e8308"
    check_user_inventory(user_id)
