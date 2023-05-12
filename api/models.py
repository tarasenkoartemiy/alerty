from django.db import models
from django.utils.translation import gettext_lazy as _


class City(models.Model):
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()


class User(models.Model):
    class Language(models.TextChoices):
        RUSSIAN = "ru", _("Russian")
        ENGLISH = "en", _("English")

    class Step(models.TextChoices):
        ENTER_REMINDER = "enter_reminder", _("enter_reminder")
        CHANGE_TEXT = "change_text", _("change_text")
        CHANGE_DATETIME = "change_datetime", _("change_datetime")
        ADD_DATETIME = "add_datetime", _("add_datetime")
        CHANGE_CITY = "change_city", _("change_city")

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    username = models.CharField(max_length=32)
    lang_code = models.CharField(max_length=2, choices=Language.choices)
    step = models.CharField(max_length=15, choices=Step.choices)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='users')


class Reminder(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("draft")
        ACTIVE = "active", _("active")
        INACTIVE = "inactive", _("inactive")
        DONE = "done", _("done")
        DELETED = "deleted", _("deleted")
        EXPIRED = "expired", _("expired")
        REDACTING = "redacting", _("redacting")

    text = models.TextField()
    datetime = models.DateTimeField(null=True)
    status = models.CharField(max_length=9, choices=Status.choices)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reminders')
