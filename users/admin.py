from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Allergen, DietaryRequirement, UserSettings
from django.contrib import admin

# Register your models here.


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ('api_tag', 'allergen_name')
    search_fields = ('allergen_name', 'api_tag')

@admin.register(DietaryRequirement)
class DietaryRequirementAdmin(admin.ModelAdmin):
    list_display = ('api_tag', 'requirement_name')
    search_fields = ('requirement_name', 'api_tag')

class UserSettingsInline(admin.StackedInline):
    model = UserSettings
    can_delete = False
    verbose_name_plural = 'Settings'
    filter_horizontal = ('allergens', 'dietary_requirements',)
    fieldsets = (
        (None, {
            'fields': (
                ('language_preference', 'prioritise_local_results'),
                ('show_nutri_score', 'show_eco_score'),
            )
        }),
        ('Dietary & Allergen Preferences', {
            'fields': ('allergens', 'dietary_requirements',),
        }),
    )

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [UserSettingsInline] 
    
    fieldsets = UserAdmin.fieldsets + (
        ('Product Preferences', {'fields': ('favourited_products',)}),
    )
    
    filter_horizontal = UserAdmin.filter_horizontal + ('favourited_products',)