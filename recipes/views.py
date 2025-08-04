from google import genai
from django.shortcuts import render
from .models import SuggestedRecipe 
from pantry.models import PantryItem 
from recipes import utils

# Create your views here.

def recipes_view(request):
    return render(request, 'recipes/recipes.html')
