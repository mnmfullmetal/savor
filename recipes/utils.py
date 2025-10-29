import json
from google import genai
from pantry.models import PantryItem, Pantry

# defines the JSON schema that the Google Gemini API must follow for its response
# this ensures that the AI's output is structured and predictable, making it easy to parse and save to the database
RECIPES_ARRAY_SCHEMA = {
    "type": "array",
    "items": {
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
}

# initialise AI client
client = genai.Client()

def generate_recipe_suggestions(user, num_recipes=3):
    """
    Generates recipe suggestions by calling the Google Gemini AI.

    Constructs a prompt based on the user's current pantry items and sends it
    to the Gemini API, requesting a structured JSON response that conforms to
    RECIPES_ARRAY_SCHEMA.
    """
    pantry = Pantry.objects.get(user=user)
    pantry_items = PantryItem.objects.filter(pantry=pantry).values_list('product__product_name', flat=True)
    pantry_item_names = ', '.join(pantry_items)
    
    # create prompt for AI
    prompt = f"Create {num_recipes} unique, healthy, and easy-to-follow recipes. For each recipe, use a selection of ingredients **only** from this list: {pantry_item_names}. Do not use any ingredients not on this list."
    responses = []

    # try recieving a response using generate_content method of the AI client object using defined configurations
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": RECIPES_ARRAY_SCHEMA,
            },
        )
    
        responses = json.loads(response.text)
        return responses, prompt
    
    except Exception as e:
        print(f"Error generating recipes: {e}")
        return [], prompt
