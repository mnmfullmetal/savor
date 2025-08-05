import json
from google import genai
from pantry.models import PantryItem

client = genai.Client()

# In your recipes/utils.py

RECIPE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "The title of the recipe."
        },
        "ingredients": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the ingredient."},
                    "quantity": {"type": "number", "description": "The quantity of the ingredient."},
                    "unit": {"type": "string", "description": "The unit of measurement (e.g., 'cup', 'tsp', 'g')."}
                },
                "required": ["name", "quantity", "unit"]
            },
            "description": "A list of ingredients with their quantities and units."
        },
        "instructions": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "A single step in the recipe's instructions."
            },
            "description": "A list of step-by-step instructions for the recipe."
        }
    },
    "required": ["title", "ingredients", "instructions"]
}

def generate_recipe_suggestions(user, num_recipes=3):
    pantry_items = PantryItem.objects.filter(user=user).values_list('product__product_name', flat=True)
    pantry_item_names = ', '.join(pantry_items)
    
    prompt =  prompt = f"Create {num_recipes} unique, detailed, and healthy recipes using only these ingredients: {pantry_item_names}. Focus on making them delicious and easy to follow."
    responses = []

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": RECIPE_SCHEMA,
            },
        )

        responses = json.loads(response.text)
        return responses
    
    except Exception as e:
        print(f"Error generating recipes: {e}")
        return []

   



    


