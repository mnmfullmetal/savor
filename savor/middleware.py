
from django.core.cache import cache
from pantry.signals import schedule_recipe_generation_task 
from django.utils import translation
from .utils import LANGUAGE_CODE_MAP 

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
    
class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'settings'):

            user_language = request.user.settings.language_preference
            
            
            if user_language:
                language_code = LANGUAGE_CODE_MAP.get(user_language)

                if language_code:
                    translation.activate(language_code)
                    request.session['_language'] = language_code
        
        response = self.get_response(request)
        return response