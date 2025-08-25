from django.db import models
from django.contrib.auth.models import AbstractUser 

# Create your models here.

class User(AbstractUser):
    favourited_products = models.ManyToManyField('pantry.Product', related_name='favourited_by')

    def __str__(self):
        return self.username
    
