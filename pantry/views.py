import json
import requests 
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django_ratelimit.exceptions import Ratelimited
from django.shortcuts import render
from pantry.forms import ProductSearchForm 
from .utils import (
    check_db_for_product,
    fetch_product_by_barcode,
    search_products_by_name,
    save_product_to_db,
)


# Create your views here.

def index(request):
    form = ProductSearchForm(request.GET)
    return render(request, 'pantry/index.html', {
        "user": request.user,
        "product_search_form": form
    })


def rate_limit_error_response(request, exception):
    return JsonResponse(
        {
            'error': 'Too Many Requests',
            'message': 'You have exceeded the search rate limit. Please wait a moment and try again.',
            'details': f'Rate limit: {exception.rate}, remaining: {exception.limit - exception.count}'
        },
        status=429
    )

@require_POST
def search_product(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)

    form = ProductSearchForm(data)

    if form.is_valid():
        barcode = form.cleaned_data.get('barcode')
        product_name = form.cleaned_data.get('product_name')

        db_products = check_db_for_product(barcode=barcode, name=product_name)

        if db_products:
            print("Returning product(s) from local DB.")
            return JsonResponse({'products': db_products})
        else:
            print("Product(s) not found in local DB. Attempting to call Open Food Facts API.")

        off_products_data = [] 

        try:
            if barcode:
                response_data = fetch_product_by_barcode(request, barcode)
                if response_data.get('status') == 1 and response_data.get('product'):
                    off_product = response_data['product']
                    saved_product = save_product_to_db(off_product) 
                    if saved_product:
                        off_products_data.append({
                            'code': saved_product.code,
                            'product_name': saved_product.product_name,
                            'brands': saved_product.brands,
                            'image_url': saved_product.image_url,
                        })
                else:
                    print(f"No product found on OFF for barcode: {barcode}. Response: {response_data}")
                    return JsonResponse({'products': []})

            elif product_name:
                response_data = search_products_by_name(request, product_name)
                if response_data.get('products'):
                    for off_prod in response_data['products']:
                        saved_product = save_product_to_db(off_prod) 
                        if saved_product:
                            off_products_data.append({
                                'code': saved_product.code,
                                'product_name': saved_product.product_name,
                                'brands': saved_product.brands,
                                'image_url': saved_product.image_url,
                            })
                else:
                    print(f"No products found on OFF for name: {product_name}. Response: {response_data}")
                    return JsonResponse({'products': []})

            else:
                return JsonResponse({'error': 'No valid search criteria provided.'}, status=400)

            return JsonResponse({'products': off_products_data})

        except Ratelimited as e:
            return rate_limit_error_response(request, e)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error fetching from OFF API: {e}")
            if e.response.status_code == 404:
                return JsonResponse({'error': 'Product not found on Open Food Facts.', 'details': 'The external API returned a 404 Not Found.'}, status=404)
            return JsonResponse({'error': 'Error fetching products from external API.', 'details': str(e)}, status=503)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection Error to OFF API: {e}")
            return JsonResponse({'error': 'Could not connect to the external API. Please check your internet connection.', 'details': str(e)}, status=503)
        except requests.exceptions.Timeout as e:
            print(f"Timeout Error from OFF API: {e}")
            return JsonResponse({'error': 'The external API took too long to respond. Please try again.', 'details': str(e)}, status=503)
        except requests.exceptions.RequestException as e:
            print(f"Generic Request Error from OFF API: {e}")
            return JsonResponse({'error': 'An unexpected error occurred while communicating with the external API.', 'details': str(e)}, status=503)
        except Exception as e:
            print(f"An unexpected error occurred in search_product: {e}")
            return JsonResponse({'error': 'An unexpected server error occurred.'}, status=500)

    else:
        print(f"Form validation failed: {form.errors}")
        return JsonResponse({'errors': form.errors}, status=400)