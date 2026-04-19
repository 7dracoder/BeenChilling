#!/usr/bin/env python3
"""Add simple single-ingredient recipes to Supabase."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fridge_observer.supabase_client import get_supabase

SIMPLE_RECIPES = [
    {
        "name": "Simple Scrambled Eggs",
        "description": "Classic scrambled eggs - perfect for any meal.",
        "cuisine": "American",
        "dietary_tags": ["vegetarian", "gluten-free"],
        "prep_minutes": 5,
        "instructions": "1. Whisk eggs with a pinch of salt. 2. Heat butter in a pan over medium-low heat. 3. Pour in eggs and gently stir until soft curds form. 4. Remove from heat while still slightly creamy. 5. Serve immediately.",
        "image_url": None,
        "ingredients": [
            {"name": "eggs", "category": "dairy", "is_pantry_staple": True},
            {"name": "butter", "category": "dairy", "is_pantry_staple": True},
        ],
    },
    {
        "name": "Sautéed Spinach",
        "description": "Quick and healthy sautéed spinach with garlic.",
        "cuisine": "Mediterranean",
        "dietary_tags": ["vegetarian", "vegan", "gluten-free"],
        "prep_minutes": 5,
        "instructions": "1. Heat olive oil in a large pan over medium heat. 2. Add fresh spinach and cook, stirring, until wilted (about 2-3 minutes). 3. Season with salt and pepper. 4. Serve as a side dish or over rice.",
        "image_url": None,
        "ingredients": [
            {"name": "spinach", "category": "vegetables", "is_pantry_staple": False},
            {"name": "olive oil", "category": "packaged_goods", "is_pantry_staple": True},
        ],
    },
    {
        "name": "Roasted Chicken Breast",
        "description": "Simple oven-roasted chicken breast with herbs.",
        "cuisine": "American",
        "dietary_tags": ["gluten-free"],
        "prep_minutes": 25,
        "instructions": "1. Preheat oven to 400°F (200°C). 2. Season chicken breast with salt, pepper, and herbs. 3. Place in baking dish and drizzle with olive oil. 4. Roast for 20-25 minutes until internal temperature reaches 165°F. 5. Let rest 5 minutes before slicing.",
        "image_url": None,
        "ingredients": [
            {"name": "chicken breast", "category": "meat", "is_pantry_staple": False},
            {"name": "olive oil", "category": "packaged_goods", "is_pantry_staple": True},
        ],
    },
    {
        "name": "Steamed Broccoli",
        "description": "Perfectly steamed broccoli - healthy and simple.",
        "cuisine": "American",
        "dietary_tags": ["vegetarian", "vegan", "gluten-free"],
        "prep_minutes": 10,
        "instructions": "1. Cut broccoli into florets. 2. Bring 1 inch of water to boil in a pot with a steamer basket. 3. Add broccoli, cover, and steam for 5-7 minutes until tender-crisp. 4. Season with salt and serve.",
        "image_url": None,
        "ingredients": [
            {"name": "broccoli", "category": "vegetables", "is_pantry_staple": False},
        ],
    },
    {
        "name": "Pan-Seared Salmon",
        "description": "Quick and easy pan-seared salmon fillet.",
        "cuisine": "American",
        "dietary_tags": ["gluten-free"],
        "prep_minutes": 12,
        "instructions": "1. Pat salmon dry and season with salt and pepper. 2. Heat oil in a pan over medium-high heat. 3. Place salmon skin-side down and cook 4-5 minutes. 4. Flip and cook 3-4 minutes more until cooked through. 5. Serve immediately.",
        "image_url": None,
        "ingredients": [
            {"name": "salmon", "category": "meat", "is_pantry_staple": False},
            {"name": "olive oil", "category": "packaged_goods", "is_pantry_staple": True},
        ],
    },
]


def main():
    sb = get_supabase()
    
    print("Adding simple recipes to Supabase...")
    
    for recipe_data in SIMPLE_RECIPES:
        # Check if recipe already exists
        existing = sb.table("recipes").select("id").eq("name", recipe_data["name"]).execute()
        if existing.data:
            print(f"  ✓ '{recipe_data['name']}' already exists, skipping")
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
        
        # Restore ingredients for next iteration
        recipe_data["ingredients"] = ingredients
    
    print(f"\n✓ Done! Added {len(SIMPLE_RECIPES)} simple recipes.")


if __name__ == "__main__":
    main()
