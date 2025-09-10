import requests
import base64
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from django.utils import timezone 
from pantry.models import Product
from django.core.cache import cache


OFF_API_BASE_URL = settings.OPENFOODFACTS_API['BASE_URL']
OFF_USER_AGENT = settings.OPENFOODFACTS_API['USER_AGENT']
USE_STAGING_AUTH = settings.OPENFOODFACTS_API['USE_STAGING_AUTH']
OFF_USERNAME = settings.OPENFOODFACTS_API['USERNAME']
OFF_PASSWORD = settings.OPENFOODFACTS_API['PASSWORD']


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

    api_url = f"{OFF_API_BASE_URL}/cgi/search.pl"
    headers = get_headers()
   
    params = {
        'search_terms': product_name,
        'search_simple': 1,
        'action': 'process',
        'json': 1
    }

    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


@ratelimit(key='ip', rate='30/m', block=True, group='off_suggestions_api_call')
def get_product_suggestions(request, query):
    
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
    
def fetch_facet_json_data():
    CATEGORIES_URL = f'{OFF_API_BASE_URL}/facets/categories.json'
    BRANDS_URL = f'{OFF_API_BASE_URL}/facets/brands.json'

    headers = get_headers()

    categories_data = {}
    brands_data = {}

    try:
        categories_response = requests.get(CATEGORIES_URL, headers=headers)
        categories_data = categories_response.json()
    except Exception as e:
        print(f"Failed to get categories from api endpoint: {e}")

    try:
        brands_response = requests.get(BRANDS_URL, headers=headers)
        brands_data = brands_response.json()
    except Exception as e:
        print(f"Failed to get brands from api endpoint: {e}")
    
    return categories_data, brands_data

def get_cached_json(data_type):
    return cache.get(f"off_{data_type}_cache")


COUNTRIES = {
    "AL": "Albania",
    "AX": "Åland Islands",
    "DZ": "Algeria",
    "AS": "American Samoa",
    "AD": "Andorra",
    "AO": "Angola",
    "AI": "Anguilla",
    "AQ": "Antarctica",
    "AG": "Antigua and Barbuda",
    "AR": "Argentina",
    "AM": "Armenia",
    "AW": "Aruba",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaijan",
    "BS": "Bahamas (the)",
    "BH": "Bahrain",
    "BD": "Bangladesh",
    "BB": "Barbados",
    "BY": "Belarus",
    "BE": "Belgium",
    "BZ": "Belize",
    "BJ": "Benin",
    "BM": "Bermuda",
    "BT": "Bhutan",
    "BO": "Bolivia (Plurinational State of)",
    "BQ": "Bonaire, Sint Eustatius and Saba",
    "BA": "Bosnia and Herzegovina",
    "BW": "Botswana",
    "BV": "Bouvet Island",
    "BR": "Brazil",
    "IO": "British Indian Ocean Territory (the)",
    "BN": "Brunei Darussalam",
    "BG": "Bulgaria",
    "BF": "Burkina Faso",
    "BI": "Burundi",
    "CV": "Cabo Verde",
    "KH": "Cambodia",
    "CM": "Cameroon",
    "CA": "Canada",
    "KY": "Cayman Islands (the)",
    "CF": "Central African Republic (the)",
    "TD": "Chad",
    "CL": "Chile",
    "CN": "China",
    "CX": "Christmas Island",
    "CC": "Cocos (Keeling) Islands (the)",
    "CO": "Colombia",
    "KM": "Comoros (the)",
    "CD": "Congo (the Democratic Republic of the)",
    "CG": "Congo (the)",
    "CK": "Cook Islands (the)",
    "CR": "Costa Rica",
    "HR": "Croatia",
    "CU": "Cuba",
    "CW": "Curaçao",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "CI": "Côte d'Ivoire",
    "DK": "Denmark",
    "DJ": "Djibouti",
    "DM": "Dominica",
    "DO": "Dominican Republic (the)",
    "EC": "Ecuador",
    "EG": "Egypt",
    "SV": "El Salvador",
    "GQ": "Equatorial Guinea",
    "ER": "Eritrea",
    "EE": "Estonia",
    "SZ": "Eswatini",
    "ET": "Ethiopia",
    "FK": "Falkland Islands (the) [Malvinas]",
    "FO": "Faroe Islands (the)",
    "FJ": "Fiji",
    "FI": "Finland",
    "FR": "France",
    "GF": "French Guiana",
    "PF": "French Polynesia",
    "TF": "French Southern Territories (the)",
    "GA": "Gabon",
    "GM": "Gambia (the)",
    "GE": "Georgia",
    "DE": "Germany",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GR": "Greece",
    "GL": "Greenland",
    "GD": "Grenada",
    "GP": "Guadeloupe",
    "GU": "Guam",
    "GT": "Guatemala",
    "GG": "Guernsey",
    "GN": "Guinea",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HT": "Haiti",
    "HM": "Heard Island and McDonald Islands",
    "VA": "Holy See (the)",
    "HN": "Honduras",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "IS": "Iceland",
    "IN": "India",
    "ID": "Indonesia",
    "IR": "Iran (Islamic Republic of)",
    "IQ": "Iraq",
    "IE": "Ireland",
    "IM": "Isle of Man",
    "IL": "Israel",
    "IT": "Italy",
    "JM": "Jamaica",
    "JP": "Japan",
    "JE": "Jersey",
    "JO": "Jordan",
    "KZ": "Kazakhstan",
    "KE": "Kenya",
    "KI": "Kiribati",
    "KP": "Korea (the Democratic People's Republic of)",
    "KR": "Korea (the Republic of)",
    "KW": "Kuwait",
    "KG": "Kyrgyzstan",
    "LA": "Lao People's Democratic Republic (the)",
    "LV": "Latvia",
    "LB": "Lebanon",
    "LS": "Lesotho",
    "LR": "Liberia",
    "LY": "Libya",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MO": "Macao",
    "MG": "Madagascar",
    "MW": "Malawi",
    "MY": "Malaysia",
    "MV": "Maldives",
    "ML": "Mali",
    "MT": "Malta",
    "MH": "Marshall Islands (the)",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MU": "Mauritius",
    "YT": "Mayotte",
    "MX": "Mexico",
    "FM": "Micronesia (Federated States of)",
    "MD": "Moldova (the Republic of)",
    "MC": "Monaco",
    "MN": "Mongolia",
    "ME": "Montenegro",
    "MS": "Montserrat",
    "MA": "Morocco",
    "MZ": "Mozambique",
    "MM": "Myanmar",
    "NA": "Namibia",
    "NR": "Nauru",
    "NP": "Nepal",
    "NL": "Netherlands (the)",
    "NC": "New Caledonia",
    "NZ": "New Zealand",
    "NI": "Nicaragua",
    "NE": "Niger (the)",
    "NG": "Nigeria",
    "NU": "Niue",
    "NF": "Norfolk Island",
    "MP": "Northern Mariana Islands (the)",
    "NO": "Norway",
    "OM": "Oman",
    "PK": "Pakistan",
    "PW": "Palau",
    "PS": "Palestine, State of",
    "PA": "Panama",
    "PG": "Papua New Guinea",
    "PY": "Paraguay",
    "PE": "Peru",
    "PH": "Philippines (the)",
    "PN": "Pitcairn",
    "PL": "Poland",
    "PT": "Portugal",
    "PR": "Puerto Rico",
    "QA": "Qatar",
    "MK": "Republic of North Macedonia",
    "RO": "Romania",
    "RU": "Russian Federation (the)",
    "RW": "Rwanda",
    "RE": "Réunion",
    "BL": "Saint Barthélemy",
    "SH": "Saint Helena, Ascension and Tristan da Cunha",
    "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia",
    "MF": "Saint Martin (French part)",
    "PM": "Saint Pierre and Miquelon",
    "VC": "Saint Vincent and the Grenadines",
    "WS": "Samoa",
    "SM": "San Marino",
    "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia",
    "SN": "Senegal",
    "RS": "Serbia",
    "SC": "Seychelles",
    "SL": "Sierra Leone",
    "SG": "Singapore",
    "SX": "Sint Maarten (Dutch part)",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "SB": "Solomon Islands",
    "SO": "Somalia",
    "ZA": "South Africa",
    "GS": "South Georgia and the South Sandwich Islands",
    "SS": "South Sudan",
    "ES": "Spain",
    "LK": "Sri Lanka",
    "SD": "Sudan (the)",
    "SR": "Suriname",
    "SJ": "Svalbard and Jan Mayen",
    "SE": "Sweden",
    "CH": "Switzerland",
    "SY": "Syrian Arab Republic",
    "TW": "Taiwan (Province of China)",
    "TJ": "Tajikistan",
    "TZ": "Tanzania, United Republic of",
    "TH": "Thailand",
    "TL": "Timor-Leste",
    "TG": "Togo",
    "TK": "Tokelau",
    "TO": "Tonga",
    "TT": "Trinidad and Tobago",
    "TN": "Tunisia",
    "TR": "Turkey",
    "TM": "Turkmenistan",
    "TC": "Turks and Caicos Islands (the)",
    "TV": "Tuvalu",
    "UG": "Uganda",
    "UA": "Ukraine",
    "AE": "United Arab Emirates (the)",
    "GB": "United Kingdom of Great Britain and Northern Ireland (the)",
    "UM": "United States Minor Outlying Islands (the)",
    "US": "United States of America (the)",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VU": "Vanuatu",
    "VE": "Venezuela (Bolivarian Republic of)",
    "VN": "Viet Nam",
    "VG": "Virgin Islands (British)",
    "VI": "Virgin Islands (U.S.)",
    "WF": "Wallis and Futuna",
    "EH": "Western Sahara",
    "YE": "Yemen",
    "ZM": "Zambia",
    "ZW": "Zimbabwe"
}