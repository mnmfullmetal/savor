import requests
import base64
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from django.utils import timezone 
from pantry.models import Product

OFF_API_BASE_URL = settings.OPENFOODFACTS_API['BASE_URL']
OFF_USER_AGENT = settings.OPENFOODFACTS_API['USER_AGENT']
USE_STAGING_AUTH = settings.OPENFOODFACTS_API['USE_STAGING_AUTH']
OFF_USERNAME = settings.OPENFOODFACTS_API['USERNAME']
OFF_PASSWORD = settings.OPENFOODFACTS_API['PASSWORD']
OFF_SEARCH_API_V3_URL = settings.OPENFOODFACTS_API['SEARCH_API_V3_URL']


def get_headers():
    headers = {"User-Agent": OFF_USER_AGENT}
    if USE_STAGING_AUTH:
        auth_string = f"{OFF_USERNAME}:{OFF_PASSWORD}".encode()
        headers["Authorization"] = f"Basic {base64.b64encode(auth_string).decode()}"
    return headers



@ratelimit(key='ip', rate='100/m', block=True, group='off_barcode_api_call')
def fetch_product_by_barcode(request, barcode):

    api_url = f"{OFF_API_BASE_URL}/api/v2/product/{barcode}.json"
    headers = get_headers()
    
    response = requests.get(api_url, headers=headers)
    response.raise_for_status() 
    return response.json()



@ratelimit(key='ip', rate='10/m', block=True, group='off_name_api_call')
def search_products_by_name(request, product_name):

    api_url = OFF_SEARCH_API_V3_URL
    headers = get_headers()

    params = {
        'query': product_name,
        'fields': 'product_name,brands,code,image_small_url,product_quantity,product_quantity_unit',
    }

    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()



def check_db_for_product(barcode = None, name = None):

    found_products_json = []

    if barcode: 
        try:
            local_product = Product.objects.get(code=barcode)
            print(f"Product found in local DB: {local_product.product_name}")
            found_products_json.append({
                 'code': local_product.code,
                 'product_name': local_product.product_name,
                 'brands': local_product.brands,
                 'image_url': local_product.image_url,
                 'product_quantity_unit': local_product.product_quantity_unit,
                 'product_quantity': local_product.product_quantity,
                 'id':local_product.id
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
                    'code': product.code,
                    'product_name': product.product_name,
                    'brands': product.brands,
                    'image_url': product.image_url,
                    'product_quantity_unit': product.product_quantity_unit,
                    'product_quantity': product.product_quantity,
                    'id':product.id
                })
            return  found_products_json
        else:
            print(f"Products not found in local DB for name: {name}. Fetching from OFF API.")
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