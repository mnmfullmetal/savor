from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.conf import settings

# Create your models here.

class User(AbstractUser):
    favourited_products = models.ManyToManyField('pantry.Product', related_name='favourited_by')

    def __str__(self):
        return self.username
    
class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')
    allergens = models.ManyToManyField('Allergen', blank=True,  related_name='allergic_to')
    dietary_requirements = models.ManyToManyField('DietaryRequirement', blank=True,  related_name='required_by_user')
    show_nutri_score = models.BooleanField(default=True)
    show_eco_score = models.BooleanField(default=True)
    country = models.CharField(max_length=25, blank=True, null=True)
    scan_to_add = models.BooleanField(default=False)
    language_preference = models.CharField(max_length=25, blank=True, null=True)
    prioritise_local_results = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Settings'


class DietaryRequirement(models.Model):
    requirement_name = models.CharField(max_length=100, unique=True)
    api_tag = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.requirement_name


class Allergen(models.Model):
    allergen_name = models.CharField(max_length=100, unique=True, help_text="User-friendly name (e.g., 'Milk')")
    api_tag = models.CharField(max_length=100, unique=True, help_text="Open Food Facts API tag (e.g., 'en:milk')")

    def __str__(self):
        return self.allergen_name
