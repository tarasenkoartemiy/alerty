from django.db import models
from django.utils.translation import gettext_lazy as _


class City(models.Model):
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self):
        return self.name


class User(models.Model):
    class Language(models.TextChoices):
        RUSSIAN = "ru", _("Russian")
        ENGLISH = "en", _("English")

    class Step(models.TextChoices):
        UPDATE_CITY = "update_city", _("update_city")
        CREATE_REMINDER = "create_reminder", _("create_reminder")
        ADD_DATETIME = "add_datetime", _("add_datetime")
        UPDATE_DATETIME = "update_datetime", _("update_datetime")
        UPDATE_TEXT = "update_text", _("update_text")

    is_bot = models.BooleanField()
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    username = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    language_code = models.CharField(max_length=2, choices=Language.choices)
    step = models.CharField(max_length=15, choices=Step.choices)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='users', null=True, blank=True)

    def __str__(self):
        return self.username


class Reminder(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", _("active")
        INACTIVE = "inactive", _("inactive")
        DONE = "done", _("done")
        DELETED = "deleted", _("deleted")
        EXPIRED = "expired", _("expired")
        REDACTING = "redacting", _("redacting")

    text = models.TextField()
    datetime = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=9, choices=Status.choices)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reminders')
