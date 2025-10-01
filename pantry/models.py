from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Sum, F, ExpressionWrapper, DecimalField 


# Create your models here.

class Pantry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pantries')
    products = models.ManyToManyField('Product', through='PantryItem', related_name='contained_in_pantries')
    nutri_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    eco_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def calculate_aggregate_scores(self):
        nutri_score_data = self.pantry_items.filter(
            product__nutrition_score__isnull=False
        ).aggregate(
            total_weighted_score=Sum(
                ExpressionWrapper(
                    F('product__nutrition_score') * F('quantity'),
                    output_field=DecimalField()
                )
            ),
            total_quantity=Sum('quantity')
        )
        
        nutri_weighted_score = nutri_score_data.get('total_weighted_score')
        nutri_total_quantity = nutri_score_data.get('total_quantity')
        new_nutri_score = None
        
        if nutri_weighted_score is not None and nutri_total_quantity and nutri_total_quantity > 0:
            new_nutri_score = nutri_weighted_score / nutri_total_quantity
            
        self.nutri_score = new_nutri_score

        eco_score_data = self.pantry_items.filter(
            product__ecoscore_score__isnull=False
        ).aggregate(
            total_weighted_score=Sum(
                ExpressionWrapper(
                    F('product__ecoscore_score') * F('quantity'),
                    output_field=DecimalField()
                )
            ),
            total_quantity=Sum('quantity')
        )

        eco_weighted_score = eco_score_data.get('total_weighted_score')
        eco_total_quantity = eco_score_data.get('total_quantity')
        new_eco_score = None
        
        if eco_weighted_score is not None and eco_total_quantity and eco_total_quantity > 0:
            new_eco_score = eco_weighted_score / eco_total_quantity
            
        self.eco_score = new_eco_score
        
        self.save()
        
    @property
    def aggregate_nutri_grade(self):
        score = self.nutri_score
        
        if score is None:
            return None
        
        if score <= -1:
            return 'A'
        elif score <= 2:
            return 'B'
        elif score <= 10:
            return 'C'
        elif score <= 18:
            return 'D'
        else:
            return 'E'

    @property
    def aggregate_eco_grade(self):
        score = self.eco_score
        
        if score is None:
            return None
        
        if score >= 80:
            return 'A'
        elif score >= 60:
            return 'B'
        elif score >= 40:
            return 'C'
        elif score >= 20:
            return 'D'
        else:
            return 'E'
        
    


class PantryItem(models.Model):
    pantry = models.ForeignKey(Pantry, on_delete=models.CASCADE, related_name='pantry_items')
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
    allergens = models.ManyToManyField('users.Allergen', blank=True, related_name="allergens_in_product")
    allergens_tags = models.JSONField(default=list, blank=True)
    labels_tags = models.JSONField(default=list, blank=True)

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


