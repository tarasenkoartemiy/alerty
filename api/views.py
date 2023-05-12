from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework import mixins
from rest_framework.response import Response

from .serializers import *
from .models import *


class CityViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class UserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer




class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    owners_queryset = User.objects.all()
    serializer_class = ReminderSerializer

    def get_personal_queryset(self):
        user = get_object_or_404(self.owners_queryset, **{self.lookup_field: self.kwargs.get(self.lookup_field, None)})
        queryset = user.reminders.all()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_personal_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
