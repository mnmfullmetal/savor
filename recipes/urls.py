from django.urls import path
from . import views

app_name = 'recipes'  

urlpatterns = [
    path('', views.recipes_view, name= 'recipes'),

    path('save_recipe/', views.save_recipe, name='save_recipe')
]
