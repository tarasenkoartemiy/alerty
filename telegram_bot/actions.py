from .generic_actions import *


def retrieve_city(pk):
    return alerty_api_request(http_method_name="get", instance_name="city", pk=pk)


def create_city(data):
    return alerty_api_request(http_method_name="post", instance_name="city", data=data)


def retrieve_user(pk):
    return alerty_api_request(http_method_name="get", instance_name="user", pk=pk)


def create_user(data):
    return alerty_api_request(http_method_name="post", instance_name="user", data=data)


def update_user(pk, data):
    return alerty_api_request(http_method_name="patch", instance_name="user", pk=pk, data=data)


def create_reminder(data):
    return alerty_api_request(http_method_name="post", instance_name="reminder", data=data)
