from django.shortcuts import render
from .models import SuggestedRecipe, Recipe, RecipeIngredient
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
import json
from django.http import JsonResponse
from pantry.models import PantryItem


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


def save_recipe(request):
    user = request.user

    if not user.is_authenticated or request.method != 'POST':
        return JsonResponse({'error': 'Invalid request or not authenticated.'}, status=400)

    try:
        data = json.loads(request.body)
        suggested_recipe_id = data.get('recipeId')
        
        if not suggested_recipe_id:
            return JsonResponse({'error': 'Missing recipeId in request body.'}, status=400)

        suggested_recipe = SuggestedRecipe.objects.get(user=user, id=suggested_recipe_id)
        recipe_data = suggested_recipe.recipe_data
        
        title = recipe_data.get("title")
        instructions = recipe_data.get("instructions")
        
        recipe = Recipe.objects.create(
            user=user,
            title=title,
            instructions=instructions,
        )

        for ingredient_data in recipe_data.get('ingredients', []):
            ingredient_name = ingredient_data.get('name')
            quantity = ingredient_data.get('quantity')
            unit = ingredient_data.get('unit')

            try:
                pantry_item = PantryItem.objects.get(pantry__user=user, product__product_name=ingredient_name)
                
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    pantry_item=pantry_item,
                    quantity=quantity,
                    unit=unit
                )
            except PantryItem.DoesNotExist:
                print(f"Warning: PantryItem for {ingredient_name} not found. Skipping.")

        suggested_recipe.status = 'saved'
        suggested_recipe.save()
        
        return JsonResponse({'success': True, 'message': 'Recipe saved successfully.'}, status=200)

    except SuggestedRecipe.DoesNotExist:
        return JsonResponse({'error': 'Suggested recipe not found.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)






