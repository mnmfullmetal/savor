from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.cache import cache
from .models import PantryItem
from recipes.tasks import generate_recipes_task

def schedule_recipe_generation_task(user):
    """
    Schedules a Celery task to generate recipes for a user, with debouncing.

    This uses two cache keys to manage task scheduling:
    - `recipe_gen_in_progress:{user.id}`: A flag to indicate that a task is
      running or was recently triggered. This is used by middleware to show a
      loading state in the UI.
    - `recipe_task_id:{user.id}`: A debounce key to prevent scheduling multiple
      tasks in rapid succession (e.g., if a user adds several items quickly).
    """
    task_key = f"recipe_task_id:{user.id}"
    cache_key = f"recipe_gen_in_progress:{user.id}"
    
    # set cache for recipe generation flag
    cache.set(cache_key, True, timeout=60)
    
    # only schedule a new task if one hasn't been scheduled in the last 10 seconds.
    if not cache.get(task_key):

        new_task = generate_recipes_task.delay(user.id)

        # set cache for debouncing 
        cache.set(task_key, new_task.id, timeout=10)



@receiver(post_save, sender=PantryItem)
@receiver(post_delete, sender=PantryItem)
def update_recipes_on_pantry_change(sender, instance, **kwargs):
    """Triggers recipe generation whenever a user's pantry is modified."""
    user = instance.pantry.user
    
    # unlock session flag to allow recipe generation 
    if hasattr(user, 'session'):
        user.session['recipes_generated_for_session'] = False
    
    schedule_recipe_generation_task(user)


@receiver(user_logged_in)
def trigger_recipes_on_login(sender, request, user, **kwargs):
    """Triggers recipe generation when a user logs in."""
    schedule_recipe_generation_task(user)
