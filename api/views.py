from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import *
from .models import *


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    http_method_names = ['get', 'post']


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'patch']

    @action(url_path='reminders', detail=False)
    def get_personal_reminders(self, request, *args, **kwargs):
        user = self.get_object()
        reminders = user.reminders.all()
        serializer = ReminderSerializer(reminders, many=True)
        return Response(serializer.data)


class ReminderViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def destroy(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
