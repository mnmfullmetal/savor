from celery import shared_task
from .models import Allergen, DietaryRequirement
from .utils import fetch_allergens_and_labels_json
from django.db.utils import IntegrityError


@shared_task
def update_allergen_and_requirement_options():
    
    relevant_dietary_tags = [
        'en:halal',
        'en:kosher',
        'en:no-lactose',
        'en:vegan',
        'en:vegetarian',
        'en:no-gluten'
    ]

    allergens_data, labels_data = fetch_allergens_and_labels_json()

    for tag in allergens_data.get('tags', []):
            api_tag = tag.get('id')
            name = tag.get('name')
            
            if api_tag and api_tag.startswith('en:'):
                try:
                    Allergen.objects.get_or_create(api_tag=api_tag, defaults={'allergen_name': name})
                except IntegrityError:
                    pass

    for tag in labels_data.get('tags', []):
            api_tag = tag.get('id')
            name = tag.get('name')
            
            if api_tag in relevant_dietary_tags:
                try:
                    DietaryRequirement.objects.get_or_create(api_tag=api_tag, defaults={'requirement_name': name})
                except IntegrityError:
                    pass
