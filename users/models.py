from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.conf import settings

# Create your models here.

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    Adds a ManyToMany relationship for favourited products, allowing users
    to bookmark products for quick access.
    """
    favourited_products = models.ManyToManyField('pantry.Product', related_name='favourited_by')

    def __str__(self):
        return self.username
    
class UserSettings(models.Model):
    """
    Stores user-specific preferences and settings.

    This model centralizes all customizable aspects of the user's experience,
    from dietary needs to UI display options and localization preferences.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')
    allergens = models.ManyToManyField('Allergen', blank=True,  related_name='allergic_to')
    dietary_requirements = models.ManyToManyField('DietaryRequirement', blank=True,  related_name='required_by_user')
    show_nutri_score = models.BooleanField(default=True)
    show_eco_score = models.BooleanField(default=True)
    # country used for localising API searches
    country = models.CharField(max_length=25, blank=True, null=True)
    scan_to_add = models.BooleanField(default=False)
    # preferred language for localised API data and UI
    language_preference = models.CharField(max_length=25, blank=True, null=True)
    # if true, API searches prioritise results from the user specified country
    prioritise_local_results = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Settings'


class DietaryRequirement(models.Model):
    """
    Represents a dietary requirement (e.g., Vegan, Halal).

    Stores both a human-readable name and the corresponding Open Food Facts API tag.
    """
    requirement_name = models.CharField(max_length=100, unique=True)
    api_tag = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.requirement_name


class Allergen(models.Model):
    """
    Represents a known allergen (e.g., Milk, Peanuts).

    Stores both a user-friendly name and the corresponding Open Food Facts API tag.
    """
    allergen_name = models.CharField(max_length=100, unique=True, help_text="User-friendly name (e.g., 'Milk')")
    api_tag = models.CharField(max_length=100, unique=True, help_text="Open Food Facts API tag (e.g., 'en:milk')")

    def __str__(self):
        return self.allergen_name
