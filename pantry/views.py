import json
import requests 
from decimal import Decimal 
from django.http import JsonResponse
from django.templatetags.static import static
from django.views.decorators.http import require_POST
from django.db.models import QuerySet
from django.contrib.auth.decorators import login_required
from django_ratelimit.exceptions import Ratelimited
from django.shortcuts import render
from pantry.forms import ProductSearchForm 
from pantry.models import Pantry, Product, PantryItem
from users.models import UserSettings
from savor.utils import LANGUAGE_CODE_MAP, COUNTRY_CODE_MAP
from savor.utils import get_cached_json, rate_limit_error_response
from .utils import (
    check_db_for_product,
    fetch_product_by_barcode,
    search_products_by_name,
    save_product_to_db,
    get_product_suggestions,
    adv_search_product,
    build_api_search_params,
    get_localised_names,
)


# Create your views here.

def index(request):
    user = request.user
    placeholder_image_url = static('media/placeholder-img.jpeg')

    if user.is_authenticated:
        
        user_settings = UserSettings.objects.get(user=user) 
        user_allergens = user_settings.allergens.all()
        user_dietary_requirements = user_settings.dietary_requirements.all()
        user_allergens_tags = set(user_allergens.values_list('api_tag', flat=True))
        user_required_tags = set(user_dietary_requirements.values_list('api_tag', flat=True))
        user_lang_name = user_settings.language_preference
        language_code = LANGUAGE_CODE_MAP.get(user_lang_name, 'en') 
                    
        processed_favourites = []
        
        for product in user.favourited_products.all():
            
            has_allergen_conflict = False
            conflicting_allergens = []
            has_dietary_mismatch = False
            missing_dietary_tags = []

            if user_settings:
                if product.allergens.filter(pk__in=user_allergens).exists():
                    has_allergen_conflict = True
                    product_allergen_tags = set(product.allergens.values_list('api_tag', flat=True)) 
                    conflicting_allergens_set = user_allergens_tags.intersection(product_allergen_tags)
                    conflicting_allergens = get_localised_names(language_code=language_code, cached_data_type='allergens', product_tags=conflicting_allergens_set) 

                product_label_tags = set(product.labels_tags or [])
                missing_dietary_tags_set = user_required_tags.difference(product_label_tags)

                if missing_dietary_tags_set:
                    has_dietary_mismatch = True
                    missing_dietary_tags = get_localised_names(language_code=language_code, cached_data_type='labels', product_tags=missing_dietary_tags_set)

            product.has_allergen_conflict = has_allergen_conflict
            product.conflicting_allergens = conflicting_allergens
            product.has_dietary_mismatch = has_dietary_mismatch
            product.missing_dietary_tags = missing_dietary_tags
            
            processed_favourites.append(product)

        user.favourited_products.all = lambda: processed_favourites 

    return render(request, 'pantry/index.html', {
        "user": user,
        'placeholder_image_url': placeholder_image_url,
        'favourite_products_list': processed_favourites,
    })


@require_POST
def pantry_search(request):
    user = request.user
    user_pantry =  Pantry.objects.get(user=user)
    user_settings = UserSettings.objects.get(user=user)
    user_allergens = user_settings.allergens.all()
    user_dietary_requirements = user_settings.dietary_requirements.all()
    user_allergens_tags = set(user_allergens.values_list('api_tag', flat=True))
    user_required_tags = set(user_dietary_requirements.values_list('api_tag', flat=True))
    user_lang_name = user_settings.language_preference
    language_code = LANGUAGE_CODE_MAP.get(user_lang_name, 'en')
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
    
    query = data.get('query').strip()
    found_items = PantryItem.objects.filter( pantry=user_pantry, product__product_name__icontains=query)

    found_items_list = []
    has_allergen_conflict = False
    has_dietary_mismatch = False
    conflicting_allergens = []
    missing_dietary_tags = []
    for item in found_items:

        product_obj = item.product

        if product_obj.allergens.filter(pk__in=user_allergens).exists():
            has_allergen_conflict = True
            product_allergen_tags = set(product_obj.allergens.values_list('api_tag', flat=True)) 
            conflicting_allergens_set = user_allergens_tags.intersection(product_allergen_tags)
            conflicting_allergens = get_localised_names(language_code=language_code, cached_data_type='allergens', product_tags=conflicting_allergens_set)

        product_label_tags = set(product_obj.labels_tags or [])

        missing_dietary_tags_set = user_required_tags.difference(product_label_tags)

        if missing_dietary_tags_set:
            has_dietary_mismatch = True
            missing_dietary_tags = get_localised_names(language_code=language_code,cached_data_type='labels', product_tags = missing_dietary_tags_set)


        found_items_list.append({
            'id': item.id,
            'quantity': str(item.quantity),
            "product_quantity": item.product.product_quantity,
            "product_quantity_unit": item.product.product_quantity_unit,
            'product_name': item.product.product_name,
            'image_url': item.product.image_url,
            'has_allergen_conflict': has_allergen_conflict,
            "conflicting_allergens": conflicting_allergens,
            'has_dietary_mismatch': has_dietary_mismatch,
            "missing_dietary_tags": missing_dietary_tags
        })

    return JsonResponse({'found_items': found_items_list})



@require_POST
def search_product(request): 

    favourite_products = set()
    user_dietary_requirements = QuerySet()
    user_allergens = QuerySet()
    language_code = 'en'
    user_allergens_tags = set()
    user_required_tags = set()
    user_settings = None
    user = request.user

    if user.is_authenticated:
        favourite_products = set(user.favourited_products.all())
        user_settings = UserSettings.objects.get(user=user)
        user_lang_name = user_settings.language_preference
        language_code = LANGUAGE_CODE_MAP.get(user_lang_name, 'en')
        user_allergens = user_settings.allergens.all()
        user_dietary_requirements = user_settings.dietary_requirements.all()
        user_allergens_tags = set(user_allergens.values_list('api_tag', flat=True))
        user_required_tags = set(user_dietary_requirements.values_list('api_tag', flat=True))
       
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
    
    ## searches the db for matching product object via barcode 
    try:
        if barcode:
            db_results = check_db_for_product(barcode=barcode)
            results = []
            if db_results:
                for result in db_results:
                        
                        product_obj = Product.objects.get(id=result['id'])
                        
                        missing_dietary_tags = [] 
                        conflicting_allergens = []
                        product_label_tags = set() 
                        result['has_dietary_mismatch'] = False
                        result['has_allergen_conflict'] = False

                        if product_obj.allergens.filter(pk__in=user_allergens).exists():
                            result['has_allergen_conflict'] = True
                            product_allergen_tags = set(product_obj.allergens.values_list('api_tag', flat=True)) 
                            conflicting_allergens_set = user_allergens_tags.intersection(product_allergen_tags)
                            conflicting_allergens = get_localised_names(language_code=language_code, cached_data_type='allergens', product_tags=conflicting_allergens_set)                               
                            result['conflicting_allergens'] = conflicting_allergens
                        
                        if user_required_tags:
                            product_label_tags = set(product_obj.labels_tags or [])
                
                        missing_dietary_tags_set = user_required_tags.difference(product_label_tags)
                        if missing_dietary_tags_set:
                            result['has_dietary_mismatch'] = True
                            missing_dietary_tags = get_localised_names(language_code=language_code, cached_data_type='labels', product_tags=missing_dietary_tags_set )
                            result['missing_dietary_tags'] = missing_dietary_tags

                        result['is_favourited'] = product_obj in favourite_products
                        result['product_name'] = product_obj.product_name 
                            
                        results.append(result)

                return JsonResponse({'products': results})
            
            ## if no db object found via barcode, fetches api results and saves the results to the db
            print(f"Calling OFF API for barcode {barcode}.")
            response_data = fetch_product_by_barcode(request, barcode)
            
            api_products = []
            if response_data.get('status') == 1 and response_data.get('product'):

                saved_product = save_product_to_db(response_data['product'])

                if saved_product:
                    has_allergen_conflict = False
                    has_dietary_mismatch = False
                    conflicting_allergens = []
                    missing_dietary_tags = []
                    product_label_tags = set() 
                    product_name = saved_product.product_name 
                    is_favourited = saved_product in favourite_products

                    if saved_product.allergens.filter(pk__in=user_allergens).exists():
                        has_allergen_conflict = True
                        product_allergen_tags = set(saved_product.allergens.values_list('api_tag', flat=True))
                        conflicting_allergens_set = user_allergens_tags.intersection(product_allergen_tags)
                        conflicting_allergens = get_localised_names(language_code=language_code, cached_data_type='allergens', product_tags=conflicting_allergens_set)
                        
                    
                    if user_required_tags:
                        product_label_tags = set(saved_product.labels_tags or [])
                
                    missing_dietary_tags_set = user_required_tags.difference(product_label_tags)

                    if missing_dietary_tags_set:
                        has_dietary_mismatch = True
                        missing_dietary_tags = get_localised_names(language_code=language_code,cached_data_type='labels', product_tags = missing_dietary_tags_set)
                    
                    api_products.append({
                        'id': saved_product.id,
                        'code': saved_product.code,
                        'product_name': saved_product.product_name,
                        'brands': saved_product.brands,
                        'image_url': saved_product.image_url,
                        'product_quantity': saved_product.product_quantity,
                        'product_quantity_unit': saved_product.product_quantity_unit,
                        'is_favourited': is_favourited,
                        'has_allergen_conflict': has_allergen_conflict,
                        'has_dietary_mismatch': has_dietary_mismatch,
                        'missing_dietary_tags': missing_dietary_tags,
                        'conflicting_allergens': conflicting_allergens,
                    })

            return JsonResponse({'products': api_products})
        
        # if no barcode supplied, fetches api results via product name and saves results to the db
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
                        conflicting_allergens = []
                        missing_dietary_tags = [] 
                        product_label_tags = set() 
                        has_dietary_mismatch = False
                        has_allergen_conflict = False

                        if saved_product.allergens.filter(pk__in=user_allergens).exists():
                            has_allergen_conflict = True
                            product_allergen_tags = set(saved_product.allergens.values_list('api_tag', flat=True))
                            conflicting_allergens_set = user_allergens_tags.intersection(product_allergen_tags)
                            conflicting_allergens = get_localised_names(language_code=language_code, cached_data_type='allergens', product_tags=conflicting_allergens_set )

                        if user_required_tags:
                            product_label_tags = set(saved_product.labels_tags or [])
                
                        missing_dietary_tags_set = user_required_tags.difference(product_label_tags)

                        if missing_dietary_tags_set:
                            has_dietary_mismatch = True
                            missing_dietary_tags = get_localised_names(language_code=language_code, cached_data_type='labels', product_tags=missing_dietary_tags_set )

                        products_found.append({
                            'id': saved_product.id,
                            'code': saved_product.code,
                            'product_name': saved_product.product_name,
                            'brands': saved_product.brands,
                            'image_url': saved_product.image_url,
                            'product_quantity': saved_product.product_quantity,
                            'product_quantity_unit': saved_product.product_quantity_unit,
                            'is_favourited': is_favourited,
                            'has_dietary_mismatch': has_dietary_mismatch,
                            'has_allergen_conflict': has_allergen_conflict,
                            'missing_dietary_tags': missing_dietary_tags,
                            'conflicting_allergens': conflicting_allergens,
                        })

                return JsonResponse({
                    'products': products_found,
                    'count': response_data.get("count", 0),
                    'page_size': response_data.get("page_size", 21),
                    'page_count': response_data.get("page", 1) 
                })
            
            ## if api call fails to fetch results via product name, falls back to local db 
            except (requests.exceptions.RequestException, Ratelimited) as e:
                print(f"API call failed during name search: {e}. Returning local db_results only.")
                db_results = check_db_for_product(search_term=product_name)
                results = []
                for result in db_results:
                    product_obj = Product.objects.get(id=result['id'])
                    missing_dietary_tags = [] 
                    conflicting_allergens = []
                    product_label_tags = set() 
                    result['has_allergen_conflict'] = False
                    result['has_dietary_mismatch'] = False

                    if product_obj.allergens.filter(pk__in=user_allergens).exists():
                            result['has_allergen_conflict'] = True
                            product_allergen_tags = set(product_obj.allergens.values_list('api_tag', flat=True)) 
                            conflicting_allergens_set = user_allergens_tags.intersection(product_allergen_tags)
                            conflicting_allergens = get_localised_names(language_code=language_code, cached_data_type='allergens', product_tags=conflicting_allergens_set)                               
                            result['conflicting_allergens'] = conflicting_allergens

                    if user_required_tags:
                            product_label_tags = set(product_obj.labels_tags or [])
                
                    missing_dietary_tags_set = user_required_tags.difference(product_label_tags)
                    if missing_dietary_tags_set:
                        result['has_dietary_mismatch'] = True
                        missing_dietary_tags = get_localised_names(language_code=language_code, cached_data_type='labels', product_tags=missing_dietary_tags_set )
                        result['missing_dietary_tags'] = missing_dietary_tags

                    result['is_favourited'] = product_obj in favourite_products
                    result['product_name'] = product_obj.product_name 
                    print(f"Local DB default name: {result['product_name']}")
                            
                    results.append(result)
                
                return JsonResponse({
                    'products': results,
                    'count': len(results),
                    'page_size': len(results), 
                    'page_count': 1 
                })
            
            ## no search criteria/ invalid criteria supplied in search parameters, return error response
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
    user = request.user
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
    if user.is_authenticated:
        favourite_products = set(user.favourited_products.all())

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
    user_settings = UserSettings.objects.get(user=request.user)
    language_name = user_settings.language_preference
    language_code = COUNTRY_CODE_MAP.get(language_name, 'en')
    categories_data = get_cached_json(language_code = language_code , data_type="categories")
    brands_data = get_cached_json(language_code = language_code, data_type="brands")
    countries_data = get_cached_json(language_code = language_code, data_type="countries")

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
    pantry.calculate_aggregate_scores()
    pantryitems = PantryItem.objects.filter(pantry=pantry)

    user_settings = UserSettings.objects.get(user=request.user)
    show_nutriscore = user_settings.show_nutri_score
    show_ecoscore = user_settings.show_eco_score
    user_allergens = user_settings.allergens.all()
    user_dietary_requirements = user_settings.dietary_requirements.all()
    user_allergens_tags = set(user_allergens.values_list('api_tag', flat=True))
    user_required_tags = set(user_dietary_requirements.values_list('api_tag', flat=True))
    user_lang_name = user_settings.language_preference
    language_code = LANGUAGE_CODE_MAP.get(user_lang_name, 'en')
    
    initial_pantry_items = PantryItem.objects.filter(pantry=pantry).select_related('product')
    placeholder_image_url = static('media/placeholder-img.jpeg')
    
    pantryitems = []
    for item in initial_pantry_items:
        product_obj = item.product 
        
        has_allergen_conflict = False
        conflicting_allergens = []
        has_dietary_mismatch = False
        missing_dietary_tags = []

        if product_obj.allergens.filter(pk__in=user_allergens).exists():
            has_allergen_conflict = True
            product_allergen_tags = set(product_obj.allergens.values_list('api_tag', flat=True)) 
            conflicting_allergens_set = user_allergens_tags.intersection(product_allergen_tags)
            conflicting_allergens = get_localised_names(language_code=language_code, cached_data_type='allergens', product_tags=conflicting_allergens_set)

        product_label_tags = set(product_obj.labels_tags or [])
        missing_dietary_tags_set = user_required_tags.difference(product_label_tags)

        if missing_dietary_tags_set:
            has_dietary_mismatch = True
            missing_dietary_tags = get_localised_names(language_code=language_code, cached_data_type='labels', product_tags = missing_dietary_tags_set)
        
        item.has_allergen_conflict = has_allergen_conflict
        item.conflicting_allergens = conflicting_allergens
        item.has_dietary_mismatch = has_dietary_mismatch
        item.missing_dietary_tags = missing_dietary_tags
        
        pantryitems.append(item)

    return render(request, "pantry/pantry.html", {
        "user" : request.user,
        "pantryitems": pantryitems,
        "pantry_nutri_grade": pantry.aggregate_nutri_grade if show_nutriscore else None,
        "pantry_eco_grade": pantry.aggregate_eco_grade if show_ecoscore else None,
        'placeholder_image_url': placeholder_image_url,
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
    user_settings = UserSettings.objects.get(user=user)
    user_allergens = user_settings.allergens.all()
    user_dietary_requirements = user_settings.dietary_requirements.all()
    user_allergens_tags = set(user_allergens.values_list('api_tag', flat=True))
    user_required_tags = set(user_dietary_requirements.values_list('api_tag', flat=True))
    user_lang_name = user_settings.language_preference
    language_code = LANGUAGE_CODE_MAP.get(user_lang_name, 'en') 

    has_allergen_conflict = False
    conflicting_allergens = []
    has_dietary_mismatch = False
    missing_dietary_tags = []

    if product.allergens.filter(pk__in=user_allergens).exists():
        has_allergen_conflict = True
        product_allergen_tags = set(product.allergens.values_list('api_tag', flat=True)) 
        conflicting_allergens_set = user_allergens_tags.intersection(product_allergen_tags)
        conflicting_allergens = get_localised_names(language_code=language_code, cached_data_type='allergens', product_tags=conflicting_allergens_set) 

    product_label_tags = set(product.labels_tags or [])
    missing_dietary_tags_set = user_required_tags.difference(product_label_tags)

    if missing_dietary_tags_set:
        has_dietary_mismatch = True
        missing_dietary_tags = get_localised_names(language_code=language_code, cached_data_type='labels', product_tags = missing_dietary_tags_set)

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
            'has_dietary_mismatch': has_dietary_mismatch,
            'missing_dietary_tags': missing_dietary_tags,
            'conflicting_allergens': conflicting_allergens,
            'has_allergen_conflict': has_allergen_conflict,
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