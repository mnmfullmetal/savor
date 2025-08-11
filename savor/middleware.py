# savor/middleware.py

from django.core.cache import cache
from pantry.signals import schedule_recipe_generation_task 

class PantryRecipeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user = request.user
            
            if not request.session.get('recipes_generated_for_session', False):
                schedule_recipe_generation_task(user)
                request.session['recipes_generated_for_session'] = True
        
        response = self.get_response(request)
        return response