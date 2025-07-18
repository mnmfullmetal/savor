from django.urls import path
from . import views

app_name = 'pantry'  

urlpatterns = [
    path('', views.index, name='index'),
]
