from django.shortcuts import render
from django.http import HttpResponse
from pantry.forms import ProductSearchForm

# Create your views here.

def index(request):
    return render(request, 'pantry/index.html', {
        "user" : request.user,
        "product_search_form": ProductSearchForm()
    })

## pantry app manages pantries 

## users app mamages accounts and authentication 

## recipes app manages the created recipes 
