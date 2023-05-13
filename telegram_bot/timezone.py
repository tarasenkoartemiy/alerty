import requests

NOMINATIM_LINK = "https://nominatim.openstreetmap.org/search?"
TIMEAPI_LINK = "https://timeapi.io/api/TimeZone/coordinate?"


def get_city(**kwargs):
    headers = {"accept-language": "en-US,en;q=0.9"}
    try:
        return requests.get(NOMINATIM_LINK, kwargs, headers=headers)
    except requests.exceptions.RequestException:
        return False


def get_timezone(**kwargs):
    try:
        return requests.get(TIMEAPI_LINK, kwargs)
    except requests.exceptions.RequestException:
        return False
