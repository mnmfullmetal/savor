from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import SuggestedRecipe, SavedRecipeIngredient, SavedRecipe 

@admin.register(SuggestedRecipe)
class SuggestedRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_user', 'created_at', 'status')
    search_fields = ( 'user__username', 'recipe_data')
    list_filter = ('status', 'created_at')

    @admin.display(description='User')
    def display_user(self, obj):
        return obj.user.username

@admin.register(SavedRecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'product', 'quantity', 'unit')
    search_fields = ('recipe__title', 'product__product_name', 'product__code')

@admin.register(SavedRecipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'display_user')
    search_fields = ('title', 'instructions', 'user__username')
    
    @admin.display(description='User')
    def display_user(self, obj):
        return obj.user.username