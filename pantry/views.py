from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from pantry.forms import ProductSearchForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from pantry.models import Product
from django.conf import settings
import json
import base64
import requests



OFF_API_CONFIG = settings.OPENFOODFACTS_API

OFF_API_BASE_URL = OFF_API_CONFIG['BASE_URL'] 
OFF_API_USERNAME = OFF_API_CONFIG['USERNAME']
OFF_API_PASSWORD = OFF_API_CONFIG['PASSWORD']
OFF_USER_AGENT = OFF_API_CONFIG['USER_AGENT']
USE_STAGING_AUTH = OFF_API_CONFIG['USE_STAGING_AUTH']

OFF_AUTH_HEADER = ""
if USE_STAGING_AUTH:
    OFF_AUTH_HEADER = "Basic " + base64.b64encode(f"{OFF_API_USERNAME}:{OFF_API_PASSWORD}".encode()).decode("ascii")


# Create your views here.

def index(request):
    form = ProductSearchForm(request.GET)
    return render(request, 'pantry/index.html', {
        "user" : request.user,
        "product_search_form": form
    })

 
def search_product(request):

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON in request body.")
    
    form = ProductSearchForm(data)

    if form.is_valid():
        barcode = form.cleaned_data.get('barcode')
        product_name = form.cleaned_data.get('product_name')
                
        headers = {
            "User-Agent": OFF_USER_AGENT,
            "Authorization": OFF_AUTH_HEADER
            }
        
        db_products  = check_db_for_product(barcode=barcode, name=product_name)

        if db_products:
            print("Returning product(s) from local DB.")
            return JsonResponse({'products': db_products})
        else:
            print("Product(s) not found in local DB. Calling Open Food Facts API.")

        headers = { "User-Agent": OFF_USER_AGENT, }
        if USE_STAGING_AUTH:
             headers["Authorization"] = OFF_AUTH_HEADER

        api_url = ""
        products_data = []

        if barcode:
             api_url = f"{OFF_API_BASE_URL}/api/v2/product/{barcode}.json"
        else:
            api_url = f"{OFF_API_BASE_URL}/cgi/search.pl?search_terms={product_name}&search_simple=1&json=1"
            
        try:
            api_response = requests.get(api_url, headers=headers)
            api_response.raise_for_status()
            response_data = api_response.json()

            if barcode:
                if response_data.get('status') == 1 and response_data.get('product'):
                    off_product = response_data['product']
                    product, created = Product.objects.update_or_create(barcode=off_product.get('code'),
                        defaults={
                            'product_name': off_product.get('product_name', None),
                            'brands': off_product.get('brands', None),
                            'image_url': off_product.get('image_small_url', None),
                            'last_updated_from_off': timezone.now(),
                            }
                        )
                        
                    print(f"Product {'created' if created else 'updated'} in local DB from OFF: {product.product_name}")

                    products_data.append({
                        'barcode': product.barcode,
                        'product_name': product.product_name,
                        'brands': product.brands,
                        'image_small_url': product.image_url,
                    })
                else:
                    print(f"Product not found on OFF API for barcode: {barcode}")
                        
            elif product_name:
                if response_data.get('products'):

                    for off_prod in response_data['products']:

                        if off_prod.get('code'):
                            product, created = Product.objects.update_or_create(
                                barcode=off_prod.get('code'),
                                defaults={
                                    'product_name': off_prod.get('product_name', None),
                                    'brands': off_prod.get('brands', None),
                                    'image_url': off_prod.get('image_small_url', None),
                                    'last_updated_from_off': timezone.now(),
                                    })
                            
                            products_data.append({
                                'barcode': product.barcode,
                                'product_name': product.product_name,
                                'brands': product.brands,
                                'image_small_url': product.image_url,
                                })

                else:
                    print(f"No products found on OFF API for name: {product_name}")
                    
            return JsonResponse({'products': products_data})

        except requests.exceptions.RequestException as e:
            print(f"Error fetching from OFF API: {e}")
            return JsonResponse({'error': 'Error fetching products from external API. Please try again later.'}, status=500)
        
    else:
        print(f"Form validation failed: {form.errors}")
        return JsonResponse({'errors': form.errors}, status=400)





def check_db_for_product(barcode = None, name = None):

    found_products_json = []

    if barcode: 
        try:
            local_product = Product.objects.get(barcode=barcode)
            print(f"Product found in local DB: {local_product.product_name}")
            found_products_json.append({
                 'barcode': local_product.barcode,
                 'product_name': local_product.product_name,
                 'brands': local_product.brands,
                 'image_small_url': product.image_url,
                })
            return found_products_json
        
        except Product.DoesNotExist:
            print(f"Product not found in local DB for barcode: {barcode}. Fetching from OFF API.")

    elif name: 
        local_products = Product.objects.filter(product_name__icontains=name)
        if local_products.exists():
            print(f"Products found in local DB for name: {name}")
            for product in local_products:
                found_products_json.append({
                    'barcode': product.barcode,
                    'product_name': product.product_name,
                    'brands': product.brands,
                    'image_small_url': product.image_url,
                })
            return  found_products_json
        
        else:
            print(f"Products not found in local DB for name: {name}. Fetching from OFF API.")
    
    return found_products_json

            
