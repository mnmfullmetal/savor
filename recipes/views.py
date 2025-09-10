from django.shortcuts import render
from .models import SuggestedRecipe, SavedRecipe, SavedRecipeIngredient
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.cache import cache
import json
from django.http import JsonResponse
from pantry.models import PantryItem, Product


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
    recently_suggested = SuggestedRecipe.objects.filter(user=user, status__in=["new", "recent"]).order_by('-created_at')
    saved_recipes = SavedRecipe.objects.filter(user=user).prefetch_related('savedrecipeingredient_set__product').order_by('-title')

    user_pantry_product_ids = set(PantryItem.objects.filter(pantry__user=user).values_list('product_id', flat=True))
    user_pantry_product_names_lower = {
        name.lower()
        for name in PantryItem.objects.filter(pantry__user=user).values_list('product__product_name', flat=True)
    }

    saved_recipes_data = []

    for recipe in saved_recipes:
        has_all_ingredients = True
        missing_ingredients = []

        for ingredient in recipe.savedrecipeingredient_set.all():
            required_product = ingredient.product
            
            if required_product.id not in user_pantry_product_ids:
                has_all_ingredients = False
                required_name = required_product.product_name.lower()

                if any(required_name in pantry_name for pantry_name in user_pantry_product_names_lower):
                    missing_ingredients.append({
                        'ingredient': ingredient,
                        'status': 'alternative_available'
                    })
                else:
                    missing_ingredients.append({
                        'ingredient': ingredient,
                        'status': 'completely_missing'
                    })
        
        saved_recipes_data.append({
            'recipe': recipe,
            'missing_ingredients': missing_ingredients,
            'has_all_ingredients': has_all_ingredients
        })

    return render(request, 'recipes/recipes.html', {
        "latest_suggestions": latest_suggestions,
        "recently_suggested": recently_suggested,
        "saved_recipes_data": saved_recipes_data,
        "recipe_gen_in_progress": recipe_gen_in_progress
    })


@require_POST
@login_required
def save_recipe(request, id):
    user = request.user

    try:
        suggested_recipe_id = id
        
        if not suggested_recipe_id:
            return JsonResponse({'error': 'Missing recipe Id in request body.'}, status=400)

        suggested_recipe = SuggestedRecipe.objects.prefetch_related('used_ingredients').get(user=user, id=suggested_recipe_id)
        recipe_data = suggested_recipe.recipe_data
        
        title = recipe_data.get("title")
        instructions = recipe_data.get("instructions")
        
        recipe = SavedRecipe.objects.create(
            user=user,
            title=title,
            instructions=instructions,
        )

        ingredient_data_dict = {item.get('name'): item for item in recipe_data.get('ingredients', [])}
        
        for product in suggested_recipe.used_ingredients.all():
            
            ingredient_info = ingredient_data_dict.get(product.product_name)
            
            if ingredient_info:
                quantity = ingredient_info.get('quantity')
                unit = ingredient_info.get('unit')
                
                SavedRecipeIngredient.objects.create(
                    recipe=recipe,
                    product=product, 
                    quantity=quantity,
                    unit=unit      
                )
            else:
                print(f"Warning: Ingredient data for {product.product_name} not found in recipe data. Skipping.")
                
        suggested_recipe.status = 'saved'
        suggested_recipe.save()

        new_recipe_data = {
            'id': recipe.id,
            'title': recipe.title,
            'ingredients': [
                {
                    'quantity': saved_ingredient.quantity,
                    'unit': saved_ingredient.unit,
                    'name': saved_ingredient.product.product_name,
                    'code': saved_ingredient.product.code
                }
                for saved_ingredient in recipe.savedrecipeingredient_set.all()
            ],
            'instructions': recipe.instructions,
        }
        
        return JsonResponse({'success': True, 'message': 'Recipe saved successfully.', 'new_recipe': new_recipe_data}, status=200)
        
    except SuggestedRecipe.DoesNotExist:
        return JsonResponse({'error': 'Suggested recipe not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@login_required
@require_POST
def mark_as_seen(request, id):
    user = request.user

    recipe = SuggestedRecipe.objects.get(user=user, id=id)

    recipe.is_seen = True
    recipe.save()

    return JsonResponse({'message': "recipe seen" })


def delete_recipe(request, id):
    user = request.user 

    recipe_to_delete = SavedRecipe.objects.get(user=user, id=id)
    recipe_to_delete.delete()

    return JsonResponse({'message': "Recipe deleted"})

