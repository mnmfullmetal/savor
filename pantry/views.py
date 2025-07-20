from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from pantry.forms import ProductSearchForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json


OFF_API_BASE_URL = "https://world.openfoodfacts.net"
OFF_API_USERNAME = "off"
OFF_API_PASSWORD = "off"
OFF_USER_AGENT = "Savor/1.0 (mnm.fullmetal@gmail.com)" 
OFF_AUTH_HEADER = "Basic "

# Create your views here.

def index(request):
    form = ProductSearchForm(request.GET)
    return render(request, 'pantry/index.html', {
        "user" : request.user,
        "product_search_form": form
    })


