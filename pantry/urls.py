from django.urls import path
from . import views

app_name = 'pantry'  

urlpatterns = [
    path('', views.index, name='index'),
    path('product/search/', views.search_product, name='search_product'),
    path("pantry/add_product", views.add_product, name = "add_product") 
]

