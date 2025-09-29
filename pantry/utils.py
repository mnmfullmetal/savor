import requests
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from django.utils import timezone 
from pantry.models import Product
from savor.utils import get_headers, rate_limit_error_response, LANGUAGE_CODE_MAP
from users.models import UserSettings

OFF_API_BASE_URL = settings.OPENFOODFACTS_API['BASE_URL']
OFF_USER_AGENT = settings.OPENFOODFACTS_API['USER_AGENT']
USE_STAGING_AUTH = settings.OPENFOODFACTS_API['USE_STAGING_AUTH']
OFF_USERNAME = settings.OPENFOODFACTS_API['USERNAME']
OFF_PASSWORD = settings.OPENFOODFACTS_API['PASSWORD']


@ratelimit(key='ip', rate='10/m', block=True, group='off_advsearch_api_call')
def adv_search_product(request, search_params, page=1):

    api_url = f"{OFF_API_BASE_URL}/cgi/search.pl"

    user = request.user
    if user.is_authenticated:
        user_settings = UserSettings.objects.get(user=user)
        if user_settings.get_only_localised_results:
         user_lang_name = user_settings.language_preference
         language_code = LANGUAGE_CODE_MAP.get(user_lang_name, 'world')
         api_url = f"https://{language_code}.openfoodfacts.net/cgi/search.pl"
        
   
    headers = get_headers()

    final_params = {
        'action': 'process',
        'json': 1,
        'page_size': 21,
        'page': page
    }

    final_params.update(search_params)

    try:
        response = requests.get(api_url, params=final_params, headers=headers)
        response.raise_for_status()         
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []




@ratelimit(key='ip', rate='100/m', block=True, group='off_barcode_api_call')
def fetch_product_by_barcode(request, barcode):

    api_url = f"{OFF_API_BASE_URL}/api/v2/product/{barcode}.json"
    headers = get_headers()
    
    response = requests.get(api_url, headers=headers)
    response.raise_for_status() 
    return response.json()



@ratelimit(key='ip', rate='10/m', block=True, group='off_name_api_call')
def search_products_by_name(request, product_name, page=1):

    user = request.user

    if user.is_authenticated:
        user_settings = UserSettings.objects.get(user=user)
        if user_settings.get_only_localised_results:
         user_lang_name = user_settings.language_preference
         language_code = LANGUAGE_CODE_MAP.get(user_lang_name, 'world')
         api_url = f"https://{language_code}.openfoodfacts.net/cgi/search.pl"
    else:
        api_url = f"{OFF_API_BASE_URL}/cgi/search.pl"

    headers = get_headers()
    params = {
        'search_terms': product_name,
        'search_simple': 1,
        'action': 'process',
        'json': 1,
        'page_size': 21,
        'page': page
    }

    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


@ratelimit(key='ip', rate='30/m', block=True, group='off_suggestions_api_call')
def get_product_suggestions(request, query):
    user_settings = UserSettings.objects.get(user=request.user)
    if user_settings.get_only_localised_results:
         user_lang_name = user_settings.language_preference
         language_code = LANGUAGE_CODE_MAP.get(user_lang_name, 'world')
         api_url = f"https://{language_code}.openfoodfacts.net/api/v3/taxonomy_suggestions"
    else:
        api_url = f"{OFF_API_BASE_URL}/api/v3/taxonomy_suggestions"
    
    params = {
        'tagtype': 'ingredients',
        'string': query,
        'limit': 5,
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('suggestions', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching suggestions: {e}")
        return []



def check_db_for_product(barcode = None, search_term = None, country=None, category= None, brand = None):
    found_products_json = []
    query_params = {}

    if barcode:
        query_params['code'] = barcode
    if search_term:
        query_params['product_name__icontains'] = search_term
    if country:
        query_params['countries_en__iexact'] = country
    if category:
        query_params['categories_en__iexact'] = category
    if brand:
        query_params['brands__iexact'] = brand

    if query_params:
        try:
            products_from_db = Product.objects.filter(**query_params)
            
            if products_from_db.exists():
                print(f"Products found in local DB for criteria: {query_params}")
                for product in products_from_db:
                    found_products_json.append({
                        'code': product.code,
                        'product_name': product.product_name,
                        'brands': product.brands,
                        'image_url': product.image_url,
                        'product_quantity_unit': product.product_quantity_unit,
                        'product_quantity': product.product_quantity,
                        'id': product.id
                    })
                return found_products_json
            else:
                print("No products found in local DB matching the criteria.")
        except Exception as e:
            print(f"An error occurred while querying the database: {e}")
    
    return found_products_json
    
            


def save_product_to_db(product_data):
   
    if not product_data or not product_data.get('code'):
        print("No valid product data or code to save to DB.")
        return None

    off_quantity = product_data.get('product_quantity')
    off_unit = product_data.get('product_quantity_unit')

    try:
        product, created = Product.objects.update_or_create(
            code=product_data.get('code'),
            defaults={
                'product_name': product_data.get('product_name'),
                'brands': product_data.get('brands'),
                'image_url': product_data.get('image_small_url'),
                'last_updated': timezone.now(),
                'product_quantity': off_quantity,
                'product_quantity_unit': off_unit,
            }
        )
        print(f"Product {'created' if created else 'updated'} in local DB: {product.product_name}")
        return product
    except Exception as e:
        print(f"Error saving product to DB: {e}")
        return None
    


def build_api_search_params(params):
 
    api_params = {}
    tag_index = 0

    if params.get('search_term'):
        api_params['search_terms'] = params['search_term']

    tag_map = {
        'country': 'countries',
        'brand': 'brands',
        'category': 'categories'
    }

    for key, tag_type in tag_map.items():
        if params.get(key):
            api_params[f'tagtype_{tag_index}'] = tag_type
            api_params[f'tag_contains_{tag_index}'] = 'exactly'
            api_params[f'tag_{tag_index}'] = params[key]
            tag_index += 1
            
    return api_params