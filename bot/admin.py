from django.contrib import admin
from django.utils import timezone
from .models import City, User, Reminder

admin.site.site_header = "Alerty"
admin.site.index_title = "This is a simple admin panel;)"


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "lat", "lon", "calculate_countryman_count"]
    ordering = ["name"]
    list_per_page = 10
    search_fields = ["name__istartswith"]

    @admin.display(description="users")
    def calculate_countryman_count(self, instance):
        return len(instance.users.all())


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "is_bot",
        "username",
        "first_name",
        "last_name",
        "created_at",
        "updated_at",
        "language_code",
        "step",
        "city",
        "calculate_reminders_count"
    ]
    ordering = ["-created_at"]
    list_per_page = 10
    search_fields = ["username__istartswith"]
    list_filter = ["is_bot", "language_code", "step", "city"]

    @admin.display(description="reminders")
    def calculate_reminders_count(self, instance):
        return len(instance.reminders.all())


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ["id", "text", "datetime", "status", "user", "calculate_remainder"]
    list_per_page = 10
    search_fields = ["text"]
    list_filter = ["status", "user"]

    @admin.display(description="remaining time")
    def calculate_remainder(self, instance):
        if instance.datetime and instance.datetime > timezone.now():
            return instance.datetime - timezone.now()
        return "-"