from django.urls import path
from . import views

app_name = 'users'  

urlpatterns = [
    path('register/', views.register, name='register'), 
    path('toggle_login/', views.toggle_login, name='toggle_login'), 
    

]
