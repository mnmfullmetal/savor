from django.shortcuts import render
from .models import SuggestedRecipe, Recipe
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def recipes_view(request):

    latest_suggestions = []
    recently_suggested = []
    saved_recipes = []

    user = request.user

    latest_suggestions = SuggestedRecipe.objects.filter(user=user, status="new").order_by('-created_at')

    recently_suggested = SuggestedRecipe.objects.filter(user=user,status__in=["new", "recent"]).order_by('-created_at')

    saved_recipes = Recipe.objects.filter(user=user).order_by('-title')

    return render(request, 'recipes/recipes.html', {
        "latest_suggestions": latest_suggestions,
        "recently_suggested": recently_suggested,
        "saved_recipes": saved_recipes

    })