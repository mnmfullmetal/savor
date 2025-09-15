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
    get_product_suggestions,
    get_cached_json,
    adv_search_product,
    build_api_search_params
)


# Create your views here.

def index(request):
    form = ProductSearchForm(request.GET)
    return render(request, 'pantry/index.html', {
        "user": request.user,
        "product_search_form": form,
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
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    barcode = form.cleaned_data.get('barcode')
    product_name = form.cleaned_data.get('product_name')
    page = data.get('page', 1)
    
    favourite_products = set()
    if request.user.is_authenticated:
        favourite_products = set(request.user.favourited_products.all())

    try:
        if barcode:
            results = check_db_for_product(barcode=barcode)
            if results:
                for result in results:
                        product_obj = Product.objects.get(id=result['id'])
                        result['is_favourited'] = product_obj in favourite_products
                return JsonResponse({'products': results})
            
            print(f"Calling OFF API for barcode {barcode}.")
            response_data = fetch_product_by_barcode(request, barcode)
            
            api_products = []
            if response_data.get('status') == 1 and response_data.get('product'):
                saved_product = save_product_to_db(response_data['product'])
                if saved_product:
                    is_favourited = saved_product in favourite_products
                    api_products.append({
                        'id': saved_product.id,
                        'code': saved_product.code,
                        'product_name': saved_product.product_name,
                        'brands': saved_product.brands,
                        'image_url': saved_product.image_url,
                        'product_quantity': saved_product.product_quantity,
                        'product_quantity_unit': saved_product.product_quantity_unit,
                        'is_favourited': is_favourited
                    })
            return JsonResponse({'products': api_products})

        elif product_name:
            
            try:
                print(f"Calling OFF API for product name '{product_name}' page {page}.")
                response_data = search_products_by_name(request, product_name, page=page)
                api_products = response_data.get('products', [])
                products_found = []
                
                for off_prod in api_products:
                    saved_product = save_product_to_db(off_prod)
                    if saved_product:
                        is_favourited = saved_product in favourite_products
                        products_found.append({
                            'id': saved_product.id,
                            'code': saved_product.code,
                            'product_name': saved_product.product_name,
                            'brands': saved_product.brands,
                            'image_url': saved_product.image_url,
                            'product_quantity': saved_product.product_quantity,
                            'product_quantity_unit': saved_product.product_quantity_unit,
                            'is_favourited': is_favourited
                        })

                return JsonResponse({
                    'products': products_found,
                    'count': response_data.get("count", 0),
                    'page_size': response_data.get("page_size", 21),
                    'page_count': response_data.get("page", 1) 
                })

            except (requests.exceptions.RequestException, Ratelimited) as e:
                print(f"API call failed during name search: {e}. Returning local results only.")
                local_results = check_db_for_product(search_term=product_name)
                
                for result in local_results:
                    product_obj = Product.objects.get(id=result['id'])
                    result['is_favourited'] = product_obj in favourite_products
                
                return JsonResponse({
                    'products': local_results,
                    'count': len(local_results),
                    'page_size': len(local_results), 
                    'page_count': 1 
                })

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


@require_POST
def advanced_product_search(request):

    try:
        data = json.loads(request.body)
        search_params = {
            'search_term': data.get('search_term'),
            'country': data.get('country'),
            'brand': data.get('brand'),
            'category': data.get('category'),
        }

        page = data.get('page', 1) 

    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request data'}, status=400)
    
    favourite_products = set()
    if request.user.is_authenticated:
        favourite_products = set(request.user.favourited_products.all())
    
    try:
        api_search_params = build_api_search_params(search_params)
        response_data = adv_search_product( request, api_search_params, page=page)

        api_products = response_data.get('products', [])
        products_found = []

        for product in api_products:
            saved_product = save_product_to_db(product)
            if saved_product:
                is_favourited = saved_product in favourite_products
                products_found.append({
                   'id': saved_product.id,
                    'code': saved_product.code,
                    'product_name': saved_product.product_name,
                    'brands': saved_product.brands,
                    'image_url': saved_product.image_url,
                    'product_quantity': saved_product.product_quantity,
                    'product_quantity_unit': saved_product.product_quantity_unit,
                    'is_favourited': is_favourited
                })
        return JsonResponse({
            'products': products_found,
            'page_count': response_data.get('page', 0),
            'count': response_data.get("count", 0),
            'page_size': response_data.get("page_size", 0)
        })
    
    except (requests.exceptions.RequestException, Ratelimited) as e:
        print(f"API call failed: {e}. Attempting local search as a fallback.")
        
        local_results = check_db_for_product(**search_params)
        
        for result in local_results:
            try:
                product_obj = Product.objects.get(id=result['id'])
                result['is_favourited'] = product_obj in favourite_products
            except Product.DoesNotExist:
                result['is_favourited'] = False

        return JsonResponse({
            'products': local_results,
            'count': len(local_results), 
            'page_size': len(local_results), 
            'page_count': 1
        })

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return JsonResponse({'error': 'An unexpected server error occurred.'}, status=500)



def populate_adv_search_criteria(request):
    categories_data = get_cached_json("categories")
    brands_data = get_cached_json("brands")
    countries_data = get_cached_json("countries")

    categories = []
    for tag in categories_data.get('tags', []):
       category_name = tag.get("name")
       categories.append(category_name)
      
    brands = []
    for tag in brands_data.get('tags', []):
       brand_name = tag.get('name')
       brands.append(brand_name)

    countries = []
    for tag in countries_data.get('tags', []):
        country_name = tag.get('name')
        countries.append(country_name)

    response_data = {
        "categories": categories,
        "brands": brands,
        "countries": countries
    }
    return JsonResponse(response_data)

    
    

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
    product = Product.objects.get(id=data.get('product_id'))

    quantity_to_add = data.get('quantityToAdd')

    quantity = Decimal(str(quantity_to_add))


    try:
        pantry_item, created = PantryItem.objects.get_or_create( pantry=pantry, product=product, defaults={'quantity': quantity})
        
        if not created:
            pantry_item.quantity += quantity 
            pantry_item.save() 
            message = f"{product.product_name} quantity updated."
        else:
            message = f"{product.product_name} added to your pantry."
            
        return JsonResponse({'message': message, 'success': True})
        
    except Exception as e:
        print(f"Error adding to pantry: {e}")
        return JsonResponse({'message': 'An unexpected error occurred.', 'success': False}, status=500)




@require_POST
@login_required
def remove_pantryitem(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
    
    quantity_to_remove = data.get('quantityToRemove')
    item = PantryItem.objects.get(id = data.get('itemId'))

    item.quantity -= Decimal(quantity_to_remove)
    item.save()

    if item.quantity <= 0:
        item.delete()
        
    return JsonResponse({'message' : f"{data['quantityToRemove']} of {item.product.product_name} has been removed", 'quantity_left': item.quantity})

    
   

def toggle_favourite_product(request, id):
    user = request.user
    product = Product.objects.get(id=id)

    if product in user.favourited_products.all():
        user.favourited_products.remove(product)
        is_favourited = False
        message = f"'{product.product_name}' unfavourited."
    else:
        user.favourited_products.add(product)
        is_favourited = True
        message = f"'{product.product_name}' favourited."

    return JsonResponse({
        'message': message,
        'is_favourited': is_favourited,
        'product': {
            'id': product.id,
            'product_name': product.product_name,
            'code': product.code,
            'brands': product.brands,
            'image_url': product.image_url,
            'product_quantity': product.product_quantity,
            'product_quantity_unit': product.product_quantity_unit,
        }
    })

def product_suggestions(request):
    try:
        query = request.GET.get('query', '').strip()

        if not query:
            return JsonResponse({'suggestions': []}) 

        suggestions_data = get_product_suggestions(request, query)

        return JsonResponse({'suggestions': suggestions_data})

    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        return JsonResponse({'error': 'Failed to get suggestions.'}, status=500)