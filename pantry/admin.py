from django.contrib import admin
from .models import Product, Pantry, PantryItem

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'code', 'brands') 
    search_fields = ('product_name', 'code', 'brands') 
    list_filter = ('brands',) 

# Admin for Pantry
@admin.register(Pantry)
class PantryAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

@admin.register(PantryItem)
class PantryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'unit', 'pantry_owner')
    list_filter = ('product', 'pantry__user__username')
    search_fields = ('product__product_name', 'product__code', 'pantry__user__username')

    @admin.display(description='Pantry Owner')
    def pantry_owner(self, obj):
        return obj.pantry.user.username