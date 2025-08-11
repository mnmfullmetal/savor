from django.shortcuts import render
from django.core.cache import cache


# Create your views here.

def recipes_view(request):
    suggested_recipes = None
    if request.user.is_authenticated:
        user = request.user

        pantry_items_list = list(user.pantryitem_set.values_list('product__product_name', flat=True))
        pantry_item_names = ', '.join(sorted(pantry_items_list))
        cache_key = f"recipes:{user.id}:{pantry_item_names}"

        suggested_recipes = cache.get(cache_key)

    return render(request, 'recipes/recipes.html', {
        "suggested_recipes": suggested_recipes
    })