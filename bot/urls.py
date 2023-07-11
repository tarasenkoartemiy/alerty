from django.urls import path
from .views import BotAPIView

urlpatterns = [
    path('webhook', BotAPIView.as_view()),
]
