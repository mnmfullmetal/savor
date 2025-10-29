from celery import shared_task
from django.contrib.auth import get_user_model
from .utils import generate_recipe_suggestions 
from .models import SuggestedRecipe
from pantry.models import PantryItem, Product
from datetime import datetime, timedelta

User = get_user_model()

@shared_task(rate_limit='10/m')
def generate_recipes_task(user_id):
    """
    Generates AI-based recipe suggestions based on a user's pantry items.

    This Celery task is triggered when a user's pantry changes. It fetches
    the user's current pantry, calls the Google Gemini API to get recipe ideas,
    and then saves them to the database. It also manages the lifecycle of
    suggestions, moving previously "new" suggestions to "recent".
    """
    user = User.objects.get(id=user_id)

    print(f"Starting recipe generation for user {user.username}...")
    pantry_items = PantryItem.objects.filter(pantry__user=user)
    item_list = pantry_items.values_list()

    # dont generate recipes if the pantry doesnt have enough items for a decent recipe
    if len(item_list) <= 3:
        print('not enough pantry items to make a recipe')
        return

    if not pantry_items.exists(): 
        print(f"Stopping recipe generation, no pantry items")
        previous_new_suggestions = SuggestedRecipe.objects.filter(user=user, status="new")
        previous_new_suggestions.update(status="deleted")
        return

    recipes_data, prompt = generate_recipe_suggestions(user)

    # move any existing "new" recipes to "recent" to remove them from the "new suggestions" section
    previous_new_suggestions = SuggestedRecipe.objects.filter(user=user, status="new")
    print(f"Found {previous_new_suggestions.count()} recipes with 'new' status.")
    previous_new_suggestions.update(status="recent")

    for recipe_data in recipes_data:
        # map ingredient names from AI response to the actual product objects from the pantry
        used_ingredient_names = [
            item['name'] for item in recipe_data.get('ingredients', [])
        ]
        
        # find the PantryItem objects that correspond to the ingredients used
        used_pantry_items = pantry_items.filter(
            product__product_name__in=used_ingredient_names
        )

        # get underlying Product objects to link to the SuggestedRecipe
        used_product_codes = used_pantry_items.values_list('product__code', flat=True)
        used_products = Product.objects.filter(code__in=used_product_codes)

        suggested_recipe = SuggestedRecipe.objects.create(
            user=user,
            prompt_text=prompt,
            recipe_data=recipe_data,
        )
        
        # create many-to-many relationship
        suggested_recipe.used_ingredients.set(used_products)
      
    print("Recipes generated and saved to the database successfully.")
    


@shared_task
def update_recent_recipes_status():
    """
    A periodic cleanup task to move old "recent" recipes to a "deleted" status.

    This runs on a schedule (defined in settings.py) to prevent the "Recently
    Suggested" list from growing indefinitely. It marks recipes older than 12
    hours as deleted, effectively removing them from the user's view.
    """
   
    time_limit = datetime.now() - timedelta(hours=12)
    
    recipes_to_update = SuggestedRecipe.objects.filter(
        status='recent',
        created_at__lte=time_limit
    )
    
    count = recipes_to_update.update(status='deleted')
    
    print(f"Celery task: Updated {count} recipes from 'recent' to 'deleted'.")
    
    return f"Task completed: {count} recipes updated."