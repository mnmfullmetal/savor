import json
import requests 
from decimal import Decimal 
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django_ratelimit.exceptions import Ratelimited
from django.shortcuts import render, redirect
from pantry.forms import ProductSearchForm 
from pantry.models import Pantry, Product, PantryItem
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
    """
    Handles product searches.
    - Barcode search: Checks local DB first, then calls the API for an exact match.
    - Name search: Combines results from the local DB and the API.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)

    form = ProductSearchForm(data)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    barcode = form.cleaned_data.get('barcode')
    product_name = form.cleaned_data.get('product_name')

    try:
        if barcode:
            results = check_db_for_product(barcode=barcode)
            if results:
                print(f"Returning barcode {barcode} from local DB.")
                return JsonResponse({'products': results})
            
            print(f"Calling OFF API for barcode {barcode}.")
            response_data = fetch_product_by_barcode(request, barcode)
            
            api_products = []
            if response_data.get('status') == 1 and response_data.get('product'):
                saved_product = save_product_to_db(response_data['product'])
                if saved_product:
                    api_products.append({
                        'id': saved_product.id,
                        'code': saved_product.code,
                        'product_name': saved_product.product_name,
                        'brands': saved_product.brands,
                        'image_url': saved_product.image_url,
                        'product_quantity': saved_product.product_quantity,
                        'product_quantity_unit': saved_product.product_quantity_unit,
                    })
            return JsonResponse({'products': api_products})

        elif product_name:
            
            combined_results = check_db_for_product(name=product_name)
            seen_codes = {p['code'] for p in combined_results if p.get('code')}

            try:
                print(f"Calling OFF API for product name '{product_name}'.")
                response_data = search_products_by_name(request, product_name)
                if response_data.get('products'):
                    for off_prod in response_data['products']:
                        saved_product = save_product_to_db(off_prod)
                        if saved_product and saved_product.code and saved_product.code not in seen_codes:
                            combined_results.append({
                                'id': saved_product.id,
                                'code': saved_product.code,
                                'product_name': saved_product.product_name,
                                'brands': saved_product.brands,
                                'image_url': saved_product.image_url,
                                'product_quantity': saved_product.product_quantity,
                                'product_quantity_unit': saved_product.product_quantity_unit,
                            })
                            seen_codes.add(saved_product.code)
            except (requests.exceptions.RequestException, Ratelimited) as e:
                print(f"API call failed during name search: {e}. Returning local results only.")
            
            return JsonResponse({'products': combined_results})

        else:
            return JsonResponse({'error': 'No valid search criteria provided.'}, status=400)

    except Ratelimited as e:
        return rate_limit_error_response(request, e)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404 and barcode:
            return JsonResponse({'products': []}) 
        print(f"HTTP Error from OFF API: {e}")
        return JsonResponse({'error': 'Error communicating with external product database.'}, status=503)
    except requests.exceptions.RequestException as e:
        print(f"Request Error from OFF API: {e}")
        return JsonResponse({'error': 'Could not connect to external product database.'}, status=503)
    except Exception as e:
        print(f"An unexpected error occurred in search_product: {e}")
        return JsonResponse({'error': 'An unexpected server error occurred.'}, status=500)

    

@login_required
def pantry_view(request):
    pantry = Pantry.objects.get(user=request.user)
    pantryitems = PantryItem.objects.filter(pantry=pantry)
    return render(request, "pantry/pantry.html", {
        "user" : request.user,
        "pantryitems": pantryitems,
    })


@require_POST
def add_product(request):

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)
     
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)

    pantry = Pantry.objects.get(user=request.user)
    product = Product.objects.get(id=data['product_id'])

    quantity_to_add = data['quantityToAdd']

    quantity = Decimal(str(quantity_to_add))
    
    pantry_item, created = PantryItem.objects.get_or_create(
        pantry=pantry,
        product=product,
        defaults={
            'quantity': quantity,
            }
        )

    if not created:
            pantry_item.quantity += quantity 
            pantry_item.save() 
            message = f"{product.product_name} quantity updated to {pantry_item.quantity}."
    else:
         message = f"{product.product_name} added to your pantry with {pantry_item.quantity} ."
        
    return JsonResponse({'message': message })




@require_POST
@login_required
def remove_pantryitem(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
    
    quantity_to_remove = data['quantityToRemove']
    item = PantryItem.objects.get(id = data['itemId'])

    item.quantity -= Decimal(quantity_to_remove)
    item.save()

    if item.quantity <= 0:
        item.delete()
        
    return JsonResponse({'message' : f"{data['quantityToRemove']} of {item.product.product_name} has been removed", 'quantity_left': item.quantity})

    
   
       
    
   