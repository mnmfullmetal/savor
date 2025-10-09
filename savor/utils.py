import requests
import base64
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

LANGUAGE_CODE_MAP = {
    'en:arabic': 'ar',
    'en:bulgarian': 'bg',
    'en:chinese': 'zh',  
    'en:czech': 'cs',
    'en:danish': 'da',
    'en:dutch': 'nl',
    'en:english': 'en',
    'en:estonian': 'et',
    'en:finnish': 'fi',
    'en:french': 'fr',
    'en:german': 'de',
    'en:greek': 'el',
    'en:hebrew': 'he',
    'en:hungarian': 'hu',
    'en:indonesian': 'id',
    'en:italian': 'it',
    'en:japanese': 'ja',
    'en:korean': 'ko',
    'en:latvian': 'lv',
    'en:lithuanian': 'lt',
    'en:norwegian': 'nb', 
    'en:polish': 'pl',
    'en:portuguese': 'pt',
    'en:romanian': 'ro',
    'en:russian': 'ru',
    'en:slovak': 'sk',
    'en:slovenian': 'sl',
    'en:spanish': 'es',
    'en:swedish': 'sv',
    'en:thai': 'th',
    'en:turkish': 'tr',
    'en:ukrainian': 'uk',
    'en:vietnamese': 'vi',
}

COUNTRY_CODE_MAP = {
    'en:algeria': 'dz',
    'en:argentina': 'ar',
    'en:australia': 'au',
    'en:austria': 'at',
    'en:belgium': 'be',
    'en:bolivia': 'bo',
    'en:brazil': 'br',
    'en:bulgaria': 'bg',
    'en:canada': 'ca',
    'en:chile': 'cl',
    'en:china': 'cn',
    'en:colombia': 'co',
    'en:costa-rica': 'cr',
    'en:cote-d-ivoire': 'ci',
    'en:croatia': 'hr',
    'en:cuba': 'cu',
    'en:cyprus': 'cy',
    'en:czech-republic': 'cz',
    'en:denmark': 'dk',
    'en:deutschland': 'de',
    'en:dominican-republic': 'do',
    'en:ecuador': 'ec',
    'en:egypt': 'eg',
    'en:english': 'en',
    'en:estonia': 'ee',
    'en:finland': 'fi',
    'en:france': 'fr',
    'en:french-polynesia': 'pf',
    'en:georgia': 'ge',
    'en:germany': 'de',
    'en:greece': 'gr',
    'en:guadeloupe': 'gp',
    'en:hong-kong': 'hk',
    'en:hungary': 'hu',
    'en:iceland': 'is',
    'en:india': 'in',
    'en:indonesia': 'id',
    'en:iraq': 'iq',
    'en:ireland': 'ie',
    'en:israel': 'il',
    'en:italy': 'it',
    'en:japan': 'jp',
    'en:kuwait': 'kw',
    'en:latvia': 'lv',
    'en:lebanon': 'lb',
    'en:lithuania': 'lt',
    'en:luxembourg': 'lu',
    'en:malaysia': 'my',
    'en:malta': 'mt',
    'en:martinique': 'mq',
    'en:mauritius': 'mu',
    'en:mexico': 'mx',
    'en:moldova': 'md',
    'en:morocco': 'ma',
    'en:netherlands': 'nl',
    'en:new-caledonia': 'nc',
    'en:new-zealand': 'nz',
    'en:norway': 'no',
    'en:pakistan': 'pk',
    'en:panama': 'pa',
    'en:peru': 'pe',
    'en:philippines': 'ph',
    'en:poland': 'pl',
    'en:portugal': 'pt',
    'en:puerto-rico': 'pr',
    'en:qatar': 'qa',
    'en:reunion': 're',
    'en:romania': 'ro',
    'en:russia': 'ru',
    'en:saudi-arabia': 'sa',
    'en:senegal': 'sn',
    'en:serbia': 'rs',
    'en:singapore': 'sg',
    'en:slovakia': 'sk',
    'en:slovenia': 'si',
    'en:south-africa': 'za',
    'en:south-korea': 'kr',
    'en:spain': 'es',
    'en:sweden': 'sv',
    'en:switzerland': 'ch',
    'en:thailand': 'th',
    'en:tunisia': 'tn',
    'en:turkey': 'tr',
    'en:ukraine': 'ua',
    'en:united-arab-emirates': 'ae',
    'en:united-kingdom': 'gb',
    'en:united-states': 'us',
    'en:uruguay': 'uy',
    'en:venezuela': 've',
    'en:vietnam': 'vn',
}

OFF_API_BASE_URL = settings.OPENFOODFACTS_API['BASE_URL']
OFF_USER_AGENT = settings.OPENFOODFACTS_API['USER_AGENT']
USE_STAGING_AUTH = settings.OPENFOODFACTS_API['USE_STAGING_AUTH']
OFF_USERNAME = settings.OPENFOODFACTS_API['USERNAME']
OFF_PASSWORD = settings.OPENFOODFACTS_API['PASSWORD']

def rate_limit_error_response(request, exception):
    return JsonResponse(
        {
            'error': 'Too Many Requests',
            'message': 'You have exceeded the search rate limit. Please wait a moment and try again.',
            'details': f'Rate limit: {exception.rate}, remaining: {exception.limit - exception.count}'
        },
        status=429
    )

def get_headers():
    headers = {"User-Agent": OFF_USER_AGENT}
    if USE_STAGING_AUTH:
        auth_string = f"{OFF_USERNAME}:{OFF_PASSWORD}".encode()
        headers["Authorization"] = f"Basic {base64.b64encode(auth_string).decode()}"
    return headers


def fetch_single_facet_json_data( facet_name):

    api_url = f'{OFF_API_BASE_URL}/facets/{facet_name}.json'
    headers = get_headers()
    response_data = {}

    try:
        response = requests.get(api_url, headers=headers)
        print(f'response from world {facet_name} endpoint: {response}')
        response.raise_for_status()
        response_data = response.json()
        return response_data
    except Exception as e:
        print(f"Failed to get categories from API endpoint: {e}")

    return response_data


def fetch_single_localised_facet_json_data(language_code, facet):

    api_url = f"https://world-{language_code}.openfoodfacts.net/facets/{facet}.json"
    headers= get_headers()
    response_data = {}
    
    try:
        response = requests.get(api_url, headers=headers)
        print(f'response from localised {facet} endpoint: {response}')
        response.raise_for_status()
        response_data = response.json()
        return response_data
    except Exception as e:
        print(f"Failed to get categories from API endpoint: {e}")

    return response_data


def get_cached_json(language_code , data_type):
    return cache.get(f"off_{data_type}_cache_{language_code }")


def get_supported_language_codes():
    return list(LANGUAGE_CODE_MAP.values())

def get_supported_country_codes():
    return list(COUNTRY_CODE_MAP.values())
