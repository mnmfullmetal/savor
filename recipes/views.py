from google import genai
from django.shortcuts import render
from .models import SuggestedRecipe 
from pantry.models import PantryItem 
from recipes.utils import generate_recipe_suggestions

# Create your views here.

def recipes_view(request):
    if request.user.is_authenticated:
        suggested_recipes =  generate_recipe_suggestions(user=request.user)
    return render(request, 'recipes/recipes.html', {
        "suggested_recipes": suggested_recipes

    })
