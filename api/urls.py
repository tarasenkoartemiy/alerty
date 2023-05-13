from django.urls import path, include
from rest_framework import routers
from .views import CityViewSet, UserViewSet, ReminderViewSet

router = routers.SimpleRouter()
router.register(r'cities', CityViewSet)
router.register(r'users', UserViewSet)
router.register(r'reminders', ReminderViewSet)

urlpatterns = [
    path('', include(router.urls))
]
