from django.contrib import admin
from .models import Product 

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'code', 'brands') 
    search_fields = ('product_name', 'code', 'brands') 
    list_filter = ('brands',) 


