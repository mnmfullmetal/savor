from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import SuggestedRecipe, RecipeIngredient

@admin.register(SuggestedRecipe)
class SuggestedRecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipe_owner', 'source', 'generation_date')
    search_fields = ('title', 'user__username', 'ingredients_list')
    list_filter = ('source',)

    @admin.display(description='User')
    def recipe_owner(self, obj):
        return obj.user.username

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient_name', 'pantry_item_match', 'suggested_recipe', 'quantity', 'unit')
    search_fields = ('ingredient_name', 'suggested_recipe__title')
    list_filter = ('pantry_item_match',)