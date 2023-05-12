from rest_framework import serializers
from .models import City, User, Reminder


class CitySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    lat = serializers.FloatField()
    lon = serializers.FloatField()

    def create(self, validated_data):
        return City.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.lat = validated_data.get("lat", instance.lat)
        instance.lon = validated_data.get("lon", instance.lon)
        instance.save()
        return instance


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=64)
    last_name = serializers.CharField(max_length=64, default="")
    username = serializers.CharField(max_length=32, default="")
    lang_code = serializers.CharField(max_length=2, default=User.Language.ENGLISH)
    step = serializers.CharField(max_length=15)
    city_id = serializers.IntegerField()

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.username = validated_data.get("username", instance.username)
        instance.lang_code = validated_data.get("lang_code", instance.lang_code)
        instance.step = validated_data.get("step", instance.step)
        instance.city_id = validated_data.get("city_id", instance.city_id)
        instance.save()
        return instance


class ReminderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    text = serializers.CharField()
    datetime = serializers.DateTimeField(default=None)
    status = serializers.CharField(max_length=9)
    user_id = serializers.IntegerField()

    def create(self, validated_data):
        return Reminder.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.text = validated_data.get("text", instance.text)
        instance.datetime = validated_data.get("datetime", instance.datetime)
        instance.status = validated_data.get("status", instance.status)
        instance.user_id = validated_data.get("user_id", instance.user_id)
        instance.save()
        return instance
