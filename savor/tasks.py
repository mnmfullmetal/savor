from celery import shared_task
from datetime import timedelta
from django.core.cache import cache
from django.db.utils import IntegrityError
from users.models import Allergen, DietaryRequirement
from .utils import fetch_single_facet_json_data, get_supported_language_codes, fetch_single_localised_facet_json_data

@shared_task
def update_facet_data():
    facets_to_fetch = ["allergens", "labels", "languages", "brands", "countries", "categories"]
    for facet in facets_to_fetch:
        fetch_and_process_facet_data.delay(facet)
    
    update_localised_facet_data.delay()

@shared_task(rate_limit='1/m')
def fetch_and_process_facet_data(facet_name):

    refresh_time =  timedelta(days=7).total_seconds()
    facet_data = fetch_single_facet_json_data(facet_name=facet_name)

    if facet_name == 'languages':
        filtered_tags = [tag for tag in facet_data.get('tags', []) if tag.get('known') == 1]
        facet_data['tags'] = filtered_tags

    cache.set(f"off_{facet_name}_cache_world", facet_data, timeout=refresh_time)
    
    relevant_dietary_tags = [
        'en:halal', 'en:kosher', 'en:no-lactose', 'en:vegan', 
        'en:vegetarian', 'en:no-gluten'
    ]


    if facet_name == 'allergens':
        for tag in facet_data.get('tags', []):
            api_tag = tag.get('id')
            name = tag.get('name')
            known = tag.get('known')
            if api_tag and api_tag.startswith('en:') and known == 1:
                try:
                    Allergen.objects.get_or_create(api_tag=api_tag, defaults={'allergen_name': name})
                except IntegrityError:
                    pass
                
    if facet_name == 'labels':
        for tag in facet_data.get('tags', []):
            api_tag = tag.get('id')
            name = tag.get('name')
        
        if api_tag in relevant_dietary_tags:
            try:
                DietaryRequirement.objects.get_or_create(api_tag=api_tag, defaults={'requirement_name': name})
            except IntegrityError:
                pass


@shared_task
def update_localised_facet_data():
    supported_languages = get_supported_language_codes()
    facets_to_fetch = ["allergens", "labels", "languages", "brands", "countries", "categories"]
    for facet in facets_to_fetch: 
        for language in supported_languages:
            fetch_and_cache_localised_facet_data.delay(language, facet)


@shared_task(rate_limit='1/m')
def fetch_and_cache_localised_facet_data(language, facet):
    refresh_time =  timedelta(days=7).total_seconds()
    facet_data = fetch_single_localised_facet_json_data(language=language, facet=facet)

    if facet == 'languages':
        filtered_tags = [tag for tag in facet_data.get('tags', []) if tag.get('known') == 1]
        facet_data['tags'] = filtered_tags


    cache.set(f"off_{facet}_cache_{language}", facet_data, timeout=refresh_time)


    

