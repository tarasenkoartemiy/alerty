from rest_framework import serializers
from .models import City, User, Reminder


class CitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = City
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = "__all__"


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = "__all__"
        read_only_fields = ["id"]
