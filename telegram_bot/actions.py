from .generic_actions import list_create_request, retrieve_update_destroy_request


def retrieve_city(pk):
    return retrieve_update_destroy_request(http_method_name="get", instance_name="city", pk=pk)


def create_city(data):
    return list_create_request(http_method_name="post", instance_name="city", data=data)


def retrieve_user(pk):
    return retrieve_update_destroy_request(http_method_name="get", instance_name="user", pk=pk)


def create_user(data):
    return list_create_request(http_method_name="post", instance_name="user", data=data)


def update_user(pk, data):
    return retrieve_update_destroy_request(http_method_name="patch", instance_name="user", pk=pk, data=data)
