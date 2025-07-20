from django.shortcuts import render
from django.http import HttpResponse
from pantry.forms import ProductSearchForm

# Create your views here.

def index(request):
    form = ProductSearchForm(request.GET)
    return render(request, 'pantry/index.html', {
        "user" : request.user,
        "product_search_form": form
    })

