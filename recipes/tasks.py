from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .utils import generate_recipe_suggestions 

User = get_user_model()

@shared_task
def generate_recipes_task(user_id, pantry_item_names):
    user = User.objects.get(id=user_id)
    cache_key = f"recipes:{user.id}:{pantry_item_names}"

    print(f"Starting recipe generation for user {user.username}...")
    recipes_data = generate_recipe_suggestions(user)
    
    cache.set(cache_key, recipes_data, timeout=86400)
