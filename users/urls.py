from django.urls import path
from . import views

app_name = 'users'  

urlpatterns = [
    path('register/', views.register, name='register'), 
    path('account_settings/', views.account_settings, name='account_settings'),
    path('delete_account/', views.delete_user, name='delete_account'),   
    
    ]
