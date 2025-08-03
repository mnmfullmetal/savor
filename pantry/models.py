from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Create your models here.

class Pantry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pantries')
    products = models.ManyToManyField('Product', through='PantryItem', related_name='contained_in_pantries')


class PantryItem(models.Model):
    pantry = models.ForeignKey(Pantry, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='pantry_entries')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_date = models.DateField(blank=True, null=True)
    added_date = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('pantry', 'product')


    def __str__(self):
        return f"{self.quantity} x {self.product.product_quantity} {self.product.product_quantity_unit}  of {self.product.product_name} in pantry of ({self.pantry.user.username})"



class Product(models.Model):
    code = models.CharField(max_length=100, unique=True)
    product_name = models.CharField(max_length=255)
    brands = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    serving_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    serving_per_container = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_quantity_unit = models.CharField(max_length=50, blank=True, null=True)
    product_quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    ingredients = models.TextField(blank=True, null=True)
    allergens = models.TextField(blank=True, null=True)


    energy_kj = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    energy_kcal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    protein_serving = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fat_serving = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    saturated_fat_serving = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    carbohydrates_serving = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sugars_serving = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fiber_serving = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sodium_serving = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    protein_100g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fat_100g = models.DecimalField(max_digits=10, decimal_places=2, blank=True,  null=True)
    saturated_fat_100g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    carbohydrates_100g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sugars_100g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fiber_100g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sodium_100g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)




    nutrition_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    nutrition_grade = models.CharField(max_length=1, blank=True, null=True)
    nova_group = models.CharField(max_length=50, blank=True, null=True)
    ecoscore_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ecoscore_grade = models.CharField(max_length=1, blank=True, null=True)
    manufacturing_location = models.CharField(max_length=255, blank=True, null=True)


    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.product_name}"


