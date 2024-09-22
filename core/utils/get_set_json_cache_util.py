import json
from django.core.cache import cache


def set_json_cache(cache_key, json_data, time_to_live):
    rendered_response = json.dumps(json_data)
    cache.set(cache_key, rendered_response, time_to_live)


def get_cache_as_json(cache_key):
    cache_response = cache.get(cache_key)

    if cache_response is None:
        return cache_response
    else:
        cache_response = json.loads(cache_response)
        return cache_response
