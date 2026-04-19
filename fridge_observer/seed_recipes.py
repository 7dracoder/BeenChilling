"""Seed 5 sample recipes into Supabase on first startup."""
import logging

logger = logging.getLogger(__name__)

SAMPLE_RECIPES = [
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
    {
        "name": "Spinach & Mushroom Omelette",
        "description": "A quick, protein-rich breakfast omelette packed with sautéed vegetables.",
        "cuisine": "French",
        "dietary_tags": ["vegetarian", "gluten-free"],
        "prep_minutes": 10,
        "instructions": "1. Whisk 3 eggs with salt and pepper. 2. Sauté mushrooms in butter over medium heat for 3 minutes until golden. 3. Add spinach and cook 1 minute until wilted. 4. Pour eggs over vegetables. 5. Cook until edges set, fold in half, serve immediately.",
        "image_url": None,
        "ingredients": [
            {"name": "eggs", "category": "dairy", "is_pantry_staple": True},
            {"name": "spinach", "category": "vegetables", "is_pantry_staple": False},
            {"name": "mushrooms", "category": "vegetables", "is_pantry_staple": False},
            {"name": "butter", "category": "dairy", "is_pantry_staple": True},
        ],
    },
    {
        "name": "Chicken Stir-Fry",
        "description": "A vibrant Asian-inspired stir-fry with tender chicken and crisp vegetables.",
        "cuisine": "Asian",
        "dietary_tags": ["gluten-free"],
        "prep_minutes": 20,
        "instructions": "1. Slice chicken breast into thin strips. 2. Heat oil in wok over high heat. 3. Stir-fry chicken 5 minutes until cooked through. 4. Add bell peppers, broccoli, and carrots, stir-fry 3 minutes. 5. Add soy sauce and sesame oil, toss to coat. 6. Serve over steamed rice.",
        "image_url": None,
        "ingredients": [
            {"name": "chicken breast", "category": "meat", "is_pantry_staple": False},
            {"name": "bell peppers", "category": "vegetables", "is_pantry_staple": False},
            {"name": "broccoli", "category": "vegetables", "is_pantry_staple": False},
            {"name": "carrots", "category": "vegetables", "is_pantry_staple": False},
            {"name": "soy sauce", "category": "packaged_goods", "is_pantry_staple": True},
            {"name": "rice", "category": "packaged_goods", "is_pantry_staple": True},
        ],
    },
    {
        "name": "Vegetable Curry",
        "description": "A warming, aromatic curry with seasonal vegetables in a rich coconut sauce.",
        "cuisine": "Indian",
        "dietary_tags": ["vegetarian", "vegan", "gluten-free"],
        "prep_minutes": 35,
        "instructions": "1. Dice onion and sauté in oil over medium heat for 5 minutes. 2. Add curry paste and cook 1 minute until fragrant. 3. Pour in coconut milk and bring to a simmer. 4. Add diced potatoes and cauliflower, cook 15 minutes. 5. Stir in spinach and cook 2 minutes. 6. Season with salt and serve with rice.",
        "image_url": None,
        "ingredients": [
            {"name": "potatoes", "category": "vegetables", "is_pantry_staple": False},
            {"name": "cauliflower", "category": "vegetables", "is_pantry_staple": False},
            {"name": "spinach", "category": "vegetables", "is_pantry_staple": False},
            {"name": "coconut milk", "category": "packaged_goods", "is_pantry_staple": True},
            {"name": "curry paste", "category": "packaged_goods", "is_pantry_staple": True},
            {"name": "onion", "category": "vegetables", "is_pantry_staple": True},
        ],
    },
    {
        "name": "Salmon with Lemon Butter",
        "description": "Pan-seared salmon fillets with a bright, tangy lemon butter sauce.",
        "cuisine": "French",
        "dietary_tags": ["gluten-free"],
        "prep_minutes": 15,
        "instructions": "1. Pat salmon fillets dry and season with salt and pepper. 2. Heat oil in pan over medium-high heat. 3. Sear salmon skin-side up for 4 minutes until golden. 4. Flip and cook 3 more minutes. 5. Remove salmon, add butter and lemon juice to pan, swirl to make sauce. 6. Pour sauce over salmon and serve with green beans.",
        "image_url": None,
        "ingredients": [
            {"name": "salmon", "category": "meat", "is_pantry_staple": False},
            {"name": "lemon", "category": "fruits", "is_pantry_staple": False},
            {"name": "butter", "category": "dairy", "is_pantry_staple": True},
            {"name": "green beans", "category": "vegetables", "is_pantry_staple": False},
        ],
    },
    {
        "name": "Pasta Primavera",
        "description": "Light and fresh pasta tossed with seasonal vegetables and Parmesan.",
        "cuisine": "Italian",
        "dietary_tags": ["vegetarian"],
        "prep_minutes": 25,
        "instructions": "1. Cook pasta in salted boiling water until al dente, reserve 1 cup pasta water. 2. Sauté zucchini in olive oil over medium heat for 3 minutes. 3. Add cherry tomatoes and cook 2 minutes until softened. 4. Add asparagus and cook 2 minutes. 5. Toss pasta with vegetables, pasta water, and olive oil. 6. Top with grated Parmesan and serve.",
        "image_url": None,
        "ingredients": [
            {"name": "pasta", "category": "packaged_goods", "is_pantry_staple": True},
            {"name": "zucchini", "category": "vegetables", "is_pantry_staple": False},
            {"name": "cherry tomatoes", "category": "vegetables", "is_pantry_staple": False},
            {"name": "asparagus", "category": "vegetables", "is_pantry_staple": False},
            {"name": "Parmesan", "category": "dairy", "is_pantry_staple": False},
        ],
    },
]


async def seed_recipes() -> None:
    """Seed sample recipes if the recipes table is empty."""
    try:
        from fridge_observer.supabase_client import get_supabase
        sb = get_supabase()

        result = sb.table("recipes").select("id", count="exact").limit(1).execute()
        if result.count and result.count > 0:
            return  # Already seeded

        for recipe_data in SAMPLE_RECIPES:
            ingredients = recipe_data.pop("ingredients")

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
                for ing in ingredients:
                    sb.table("recipe_ingredients").insert({
                        "recipe_id": recipe_id,
                        "name": ing["name"],
                        "category": ing.get("category"),
                        "is_pantry_staple": bool(ing.get("is_pantry_staple", False)),
                    }).execute()

            recipe_data["ingredients"] = ingredients

        logger.info("Seeded %d recipes into Supabase", len(SAMPLE_RECIPES))

    except Exception as exc:
        logger.warning("Recipe seeding skipped: %s", exc)
