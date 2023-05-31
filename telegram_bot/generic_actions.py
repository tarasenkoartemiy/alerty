from django.conf import settings
from django.urls import reverse

import requests


def get_url(view_name, args=None):
    path = reverse(view_name, args=args)
    return settings.BASE_URL + path


def get_detail_url(instance_name, pk):
    return get_url(f"{instance_name}-detail", args=(pk,))


def get_list_url(instance_name):
    return get_url(f"{instance_name}-list")


def decode_json(func):
    def wrapper(**kwargs):
        response = func(**kwargs)
        if response.ok:
            return response.json()

    return wrapper


@decode_json
def list_create_request(http_method_name, instance_name, data=None):
    url = get_list_url(instance_name)
    return requests.request(http_method_name, url, data=data)


@decode_json
def retrieve_update_destroy_request(http_method_name, instance_name, pk, data=None):
    url = get_detail_url(instance_name, pk)
    return requests.request(http_method_name, url, data=data)


def city_api_request(city):
    params = {"city": city, "format": "json", "limit": 1}
    headers = {"accept-language": "en-US,en;q=0.9"}
    return requests.get("https://nominatim.openstreetmap.org/search?", params, headers=headers)


def timezone_api_request(lat, lon):
    params = {"latitude": lat, "longitude": lon}
    return requests.get("https://timeapi.io/api/Time/current/coordinate?", params)
