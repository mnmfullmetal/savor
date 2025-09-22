from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Allergen, DietaryRequirement


# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass

@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ('api_tag', 'allergen_name')
    search_fields = ('allergen_name', 'api_tag')

@admin.register(DietaryRequirement)
class DietaryRequirementAdmin(admin.ModelAdmin):
    list_display = ('api_tag', 'requirement_name')
    search_fields = ('requirement_name', 'api_tag')