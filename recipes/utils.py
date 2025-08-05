from google import genai
from pantry.models import PantryItem

client = genai.Client()

def generate_recipe_suggestions(user, num_recipes=3):
    pantry_items = PantryItem.objects.filter(user=user).values_list('product__product_name', flat=True)
    
    prompt = create_recipe_prompt(pantry_items)
    responses = []

    for i in range(num_recipes):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
                )
            responses.append(response)
        except Exception as e:
            print(f"Error generating recipe: {e}")

    return responses



    

def create_recipe_prompt(pantry_items):

    pantry_item_names = ', '.join(pantry_items)
    
    # The f-string dynamically inserts the pantry_item_names into the prompt template
    prompt = f"""
You are a friendly and professional recipe generator. Your task is to create a detailed and healthy recipe based on a given list of ingredients. The user wants the recipe to be delicious, easy to follow, and realistic for a home cook.

### Instructions
1.  **Format**: Structure the recipe as a single, cohesive block of text.
2.  **Title**: The recipe must have a clear title at the top, such as "Title: [Recipe Name]".
3.  **Ingredients**: Create a bulleted list of ingredients with specific measurements. For example, "Ingredients: - 2 large eggs - 1 cup milk - 1 tablespoon butter".
4.  **Instructions**: Provide a numbered list of step-by-step instructions. Each step should be a clear, simple action.
5.  **Health**: The recipe must be focused on being healthy and should minimize processed ingredients and excessive fats or sugars where possible.

### Ingredients
{pantry_item_names}

### Output
"""
    return prompt
