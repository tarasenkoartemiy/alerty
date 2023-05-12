from django.urls import path
from .views import CityViewSet, UserViewSet, ReminderViewSet

urlpatterns = [
    path('cities', CityViewSet.as_view({"get": "list", "post": "create"})),
    path('cities/<pk>', CityViewSet.as_view({"get": "retrieve"})),
    path('users', UserViewSet.as_view({"post": "create"})),
    path('users/<pk>', UserViewSet.as_view({"get": "retrieve", "patch": "partial_update"})),
    path('users/<pk>/reminders', ReminderViewSet.as_view({"get": "list"})),
    path('reminders', ReminderViewSet.as_view({"post": "create"})),
    path('reminders/<pk>',
         ReminderViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "partial_update"}))
]
