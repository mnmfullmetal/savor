import requests
from django.conf import settings
from pantry.utils import get_headers

OFF_API_BASE_URL = settings.OPENFOODFACTS_API['BASE_URL']

def fetch_allergens_and_labels_json():

    allergens_url = f"{OFF_API_BASE_URL}/allergens.json"
    labels_url = f"{OFF_API_BASE_URL}/labels.json"
    headers = get_headers()    

    try:
        allergens_response = requests.get(allergens_url, headers=headers)
        allergens_response.raise_for_status()
        allergens_data = allergens_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching allergens: {e}")

    try:
        labels_response =  requests.get(labels_url, headers=headers)
        labels_response.raise_for_status()
        labels_data = labels_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching labels: {e}")

    return allergens_data, labels_data



def get_localised_allergens_and_requirements(country_code):
    subdomain = country_code.lower() if country_code else 'world'
    base_url = f"https://{subdomain}.openfoodfacts.org"

    localized_allergens = []
    localized_dietary_reqs = []

    try:
        allergens_url = f"{base_url}/allergens.json"
        allergens_response = requests.get(allergens_url)
        allergens_response.raise_for_status()
        localized_allergens = allergens_response.json().get('tags', [])
    except requests.exceptions.RequestException:
        pass

    try:
        labels_url = f"{base_url}/labels.json"
        labels_response = requests.get(labels_url)
        labels_response.raise_for_status()
        localized_dietary_reqs = labels_response.json().get('tags', [])
    except requests.exceptions.RequestException:
        pass

    return localized_allergens, localized_dietary_reqs