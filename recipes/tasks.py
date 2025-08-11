from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .utils import generate_recipe_suggestions 
from .models import SuggestedRecipe
from pantry.models import PantryItem
User = get_user_model()

@shared_task
def generate_recipes_task(user_id, pantry_item_names):
    user = User.objects.get(id=user_id)
    cache_key = f"recipes:{user.id}:{pantry_item_names}"

    print(f"Starting recipe generation for user {user.username}...")
    all_pantry_item_objects = PantryItem.objects.filter(user=user, product__product_name__in=pantry_item_names.split(', '))

    recipes_data, prompt = generate_recipe_suggestions(user)

    for recipe_data in recipes_data:
        used_ingredient_names = [
            item['name'] for item in recipe_data.get('ingredients', [])
        ]
        
        used_pantry_items = all_pantry_item_objects.filter(
            product__product_name__in=used_ingredient_names
        )
        
        suggested_recipe = SuggestedRecipe.objects.create(
            user=user,
            prompt_text=prompt,
            recipe_data=recipe_data,
        )
        
        suggested_recipe.used_ingredients.set(used_pantry_items)

    print("Recipes generated and saved to the database successfully.")
    
    cache.set(cache_key, recipes_data, timeout=86400)
