from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.cache import cache
from .models import PantryItem, Pantry
from recipes.tasks import generate_recipes_task
from savor.celery import app

def schedule_recipe_generation_task(user):
    
    task_key = f"recipe_task_id:{user.id}"
    
    if not cache.get(task_key):
        try:
            pantry = Pantry.objects.get(user=user)
        except Pantry.DoesNotExist:
            return

    pantry_items_list = list(pantry.pantry_items.values_list('product__product_name', flat=True))
    pantry_item_names = ', '.join(sorted(pantry_items_list))

    new_task = generate_recipes_task.apply_async(
        args=[user.id, pantry_item_names],
        countdown=5 
    )
    
    cache.set(task_key, new_task.id, timeout=10)


@receiver(post_save, sender=PantryItem)
@receiver(post_delete, sender=PantryItem)
def update_recipes_on_pantry_change(sender, instance, **kwargs):
    user = instance.pantry.user
    schedule_recipe_generation_task(user)


@receiver(user_logged_in)
def trigger_recipes_on_login(sender, request, user, **kwargs):
    schedule_recipe_generation_task(user)