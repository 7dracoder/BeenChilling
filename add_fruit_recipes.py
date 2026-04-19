#!/usr/bin/env python3
"""Add fruit-based recipes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fridge_observer.supabase_client import get_supabase

FRUIT_RECIPES = [
    {
        "name": "Baked Apple",
        "description": "Simple baked apple with cinnamon - a healthy dessert.",
        "cuisine": "American",
        "dietary_tags": ["vegetarian", "vegan", "gluten-free"],
        "prep_minutes": 30,
        "instructions": "1. Preheat oven to 350°F (175°C). 2. Core the apple, leaving the bottom intact. 3. Place in baking dish and sprinkle with cinnamon. 4. Bake for 25-30 minutes until tender. 5. Serve warm.",
        "image_url": None,
        "ingredients": [
            {"name": "apple", "category": "fruits", "is_pantry_staple": False},
            {"name": "cinnamon", "category": "packaged_goods", "is_pantry_staple": True},
        ],
    },
    {
        "name": "Fresh Apple Slices",
        "description": "Crisp apple slices - perfect healthy snack.",
        "cuisine": "American",
        "dietary_tags": ["vegetarian", "vegan", "gluten-free", "raw"],
        "prep_minutes": 2,
        "instructions": "1. Wash the apple thoroughly. 2. Cut into slices or wedges. 3. Remove core and seeds. 4. Serve immediately or with peanut butter.",
        "image_url": None,
        "ingredients": [
            {"name": "apple", "category": "fruits", "is_pantry_staple": False},
        ],
    },
    {
        "name": "Banana Smoothie",
        "description": "Quick and creamy banana smoothie.",
        "cuisine": "American",
        "dietary_tags": ["vegetarian", "gluten-free"],
        "prep_minutes": 5,
        "instructions": "1. Peel banana and break into chunks. 2. Add to blender with milk and ice. 3. Blend until smooth. 4. Pour into glass and serve immediately.",
        "image_url": None,
        "ingredients": [
            {"name": "banana", "category": "fruits", "is_pantry_staple": False},
            {"name": "milk", "category": "dairy", "is_pantry_staple": True},
        ],
    },
    {
        "name": "Fresh Orange Juice",
        "description": "Freshly squeezed orange juice - vitamin C boost.",
        "cuisine": "American",
        "dietary_tags": ["vegetarian", "vegan", "gluten-free"],
        "prep_minutes": 5,
        "instructions": "1. Cut oranges in half. 2. Squeeze juice using a juicer or by hand. 3. Strain if desired. 4. Serve immediately over ice.",
        "image_url": None,
        "ingredients": [
            {"name": "orange", "category": "fruits", "is_pantry_staple": False},
        ],
    },
    {
        "name": "Sliced Strawberries",
        "description": "Fresh strawberries - sweet and healthy.",
        "cuisine": "American",
        "dietary_tags": ["vegetarian", "vegan", "gluten-free", "raw"],
        "prep_minutes": 3,
        "instructions": "1. Rinse strawberries under cold water. 2. Remove stems and leaves. 3. Slice into halves or quarters. 4. Serve fresh or with yogurt.",
        "image_url": None,
        "ingredients": [
            {"name": "strawberry", "category": "fruits", "is_pantry_staple": False},
        ],
    },
]

def main():
    sb = get_supabase()
    
    print("Adding fruit-based recipes...\n")
    
    for recipe_data in FRUIT_RECIPES:
        # Check if exists
        existing = sb.table("recipes").select("id").eq("name", recipe_data["name"]).execute()
        if existing.data:
            print(f"  ✓ '{recipe_data['name']}' already exists")
            continue
        
        ingredients = recipe_data.pop("ingredients")
        
        # Insert recipe
        recipe_result = sb.table("recipes").insert({
            "name": recipe_data["name"],
            "description": recipe_data["description"],
            "cuisine": recipe_data["cuisine"],
            "dietary_tags": recipe_data["dietary_tags"],
            "prep_minutes": recipe_data["prep_minutes"],
            "instructions": recipe_data["instructions"],
            "image_url": recipe_data.get("image_url"),
        }).execute()
        
        if recipe_result.data:
            recipe_id = recipe_result.data[0]["id"]
            
            # Insert ingredients
            for ing in ingredients:
                sb.table("recipe_ingredients").insert({
                    "recipe_id": recipe_id,
                    "name": ing["name"],
                    "category": ing.get("category"),
                    "is_pantry_staple": bool(ing.get("is_pantry_staple", False)),
                }).execute()
            
            print(f"  ✓ Added '{recipe_data['name']}'")
        
        recipe_data["ingredients"] = ingredients
    
    print(f"\n✓ Done! Added {len(FRUIT_RECIPES)} fruit recipes.")

if __name__ == "__main__":
    main()
