from django.urls import path
from . import views

app_name = 'recipes'  

urlpatterns = [
    path('', views.recipes_view, name= 'recipes'),

    path('save_recipe/<int:id>', views.save_recipe, name='save_recipe'),
    path('mark_as_seen/<int:id>/', views.mark_as_seen, name='mark_as_seen')
]
