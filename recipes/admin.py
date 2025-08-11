from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import SuggestedRecipe, RecipeIngredient, Recipe 

@admin.register(SuggestedRecipe)
class SuggestedRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_user', 'created_at', 'status')
    search_fields = ( 'user__username', 'recipe_data')
    list_filter = ('status', 'created_at')

    @admin.display(description='User')
    def display_user(self, obj):
        return obj.user.username

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'pantry_item', 'quantity', 'unit')
    search_fields = ('recipe__title', 'pantry_item__product__product_name')

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'display_user')
    search_fields = ('title', 'instructions', 'user__username')
    
    @admin.display(description='User')
    def display_user(self, obj):
        return obj.user.username