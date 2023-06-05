from django.conf import settings
from django.urls import reverse
import requests


def get_url(instance_name, pk):
    path = reverse(f"{instance_name}-detail", args=(pk,)) if pk else reverse(f"{instance_name}-list")
    return settings.BASE_URL + path


def decode_json(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.ok and response.headers.get("Content-Type", "").startswith("application/json"):
            return response.json()

    return wrapper


@decode_json
def alerty_api_request(http_method_name, instance_name, **kwargs):
    pk = kwargs.pop("pk", None)
    url = get_url(instance_name, pk)
    return requests.request(http_method_name, url, **kwargs)


@decode_json
def city_api_request(city):
    params = {"city": city, "format": "json", "limit": 1}
    headers = {"accept-language": "en-US,en;q=0.9"}
    return requests.get("https://nominatim.openstreetmap.org/search?", params, headers=headers)


@decode_json
def timezone_api_request(lat, lon):
    params = {"latitude": lat, "longitude": lon}
    return requests.get("https://timeapi.io/api/Time/current/coordinate?", params)