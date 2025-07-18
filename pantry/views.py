from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse ("welcome to Savor!")

## pantry app manages pantries 

## users app mamages accounts and authentication 

## recipes app manages the created recipes 
