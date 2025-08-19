from django.db import models
from django.conf import settings

# Create your models here.

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    pantry_item = models.ForeignKey('pantry.PantryItem', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)

    class Meta:
        unique_together = ('recipe', 'pantry_item')

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.pantry_item.product.product_name} for {self.recipe.title}"
    
    
class Recipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=255, blank=True, null=True)
    instructions = models.JSONField()
    ingredients = models.ManyToManyField('pantry.PantryItem', through='RecipeIngredient', related_name='used_in_recipes')


class SuggestedRecipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='suggested_recipes')
    prompt_text = models.TextField() 
    recipe_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    used_ingredients = models.ManyToManyField('pantry.PantryItem', related_name='suggested_recipes_used_in')
    is_seen = models.BooleanField(default=False) 


    STATUS_CHOICES = [
        ('new', 'New'),
        ('recent', 'Recent'),
        ('saved', 'Saved'),
        ('deleted', 'Deleted')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f"Suggestion for {self.user.username} ({self.status})"