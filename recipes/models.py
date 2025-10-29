from django.db import models
from django.conf import settings

# Create your models here.

class SavedRecipeIngredient(models.Model):
    """
    Through model for `SavedRecipe` to `Product`, storing specific ingredient
    quantities and units for a saved recipe.
    """
    recipe = models.ForeignKey('SavedRecipe', on_delete=models.CASCADE)
    product = models.ForeignKey('pantry.Product', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)

    class Meta:
        # ensures that a product can only be listed once per recipe
        unique_together = ('recipe', 'product')

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.product.product_name} for {self.recipe.title}"
    
    
class SavedRecipe(models.Model):
    """
    Represents a recipe that a user has explicitly saved.

    This model stores the structured recipe data (title, instructions) and
    links to the specific `Product`s from the pantry that are used as ingredients.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=255, blank=True, null=True)
    # instructions are stored as a JSON array
    instructions = models.JSONField()
    # many-to-many relationship to "Product" through "SavedRecipeIngredient" to store detailed ingredient information
    ingredients = models.ManyToManyField('pantry.Product', through='SavedRecipeIngredient', related_name='used_in_recipes')


class SuggestedRecipe(models.Model):
    """
    Stores AI-generated recipe suggestions for a user.

    This model captures the raw AI output and tracks the lifecycle of a
    suggestion (new, recent, saved, deleted) to manage what the user sees.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='suggested_recipes')
    # the original prompt sent to the AI for generating this recipe
    prompt_text = models.TextField() 
    # the raw JSON response from the AI
    recipe_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    # products from the user's pantry that were used in this suggestion
    used_ingredients = models.ManyToManyField('pantry.Product', related_name='suggested_recipes_used_in')
    # flag to indicate if the user has expanded and viewed this suggestion
    is_seen = models.BooleanField(default=False) 


    # status of the suggestion, managing its state
    # 'new': freshly generated, 'recent': seen but not saved, 'saved': recipe saved (as SavedRecipe object), 'deleted': no longer shown.
    STATUS_CHOICES = [
        ('new', 'New'),
        ('recent', 'Recent'),
        ('saved', 'Saved'),
        ('deleted', 'Deleted')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f"Suggestion for {self.user.username} ({self.status})"