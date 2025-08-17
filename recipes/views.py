from django.shortcuts import render
from .models import SuggestedRecipe, Recipe
from django.contrib.auth.decorators import login_required
from django.core.cache import cache


# Create your views here.

@login_required
def recipes_view(request):
    user = request.user

    cache_key = f"recipe_gen_in_progress:{user.id}"
    latest_suggestions = []
    recently_suggested = []
    saved_recipes = []

    recipe_gen_in_progress = False

    if cache.get(cache_key):
        recipe_gen_in_progress = True
        cache.delete(cache_key)

    latest_suggestions = SuggestedRecipe.objects.filter(user=user, status="new").order_by('-created_at')

    recently_suggested = SuggestedRecipe.objects.filter(user=user,status__in=["new", "recent"]).order_by('-created_at')

    saved_recipes = Recipe.objects.filter(user=user).order_by('-title')


    return render(request, 'recipes/recipes.html', {
        "latest_suggestions": latest_suggestions,
        "recently_suggested": recently_suggested,
        "saved_recipes": saved_recipes,
        "recipe_gen_in_progress": recipe_gen_in_progress

    })