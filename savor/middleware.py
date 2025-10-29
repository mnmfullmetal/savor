
from django.core.cache import cache
from pantry.signals import schedule_recipe_generation_task 
from django.utils import translation
from .utils import LANGUAGE_CODE_MAP 

class PantryRecipeMiddleware:
    """
    Triggers AI recipe generation once per user session upon login.

    This middleware checks a session flag on each request. If the flag is not
    set (indicating a new session), it schedules a recipe generation task and
    then sets the flag to 'lock' itself for the remainder of the session.
    This ensures recipes are generated on login without re-triggering on every
    subsequent page load. The flag is 'unlocked' by signals when the pantry
    changes, preparing the middleware for the next login.
    """
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
    """
    Sets the application's language based on the authenticated user's profile settings.

    On each request, this middleware checks the user's saved language preference,
    activates the corresponding translation, and stores it in the session for
    other parts of Django (like LocaleMiddleware) to use.
    """
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