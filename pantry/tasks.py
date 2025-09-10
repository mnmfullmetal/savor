from celery import shared_task
from datetime import timedelta
from django.core.cache import cache
from .utils import fetch_facet_json_data

@shared_task
def update_facet_json_data():
    refresh_time =  timedelta(days=7).total_seconds()
    categories_data, brands_data = fetch_facet_json_data()
    cache.set("off_brands_cache", brands_data, timeout=refresh_time )
    cache.set("off_categories_cache", categories_data, timeout=refresh_time )