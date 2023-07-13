from alerty.celery_app import app
from django.utils import timezone, translation
from .models import Reminder
from .handlers import bot
from .values import Phrase


@app.task
def check_reminders():
    reminders = (
        Reminder.objects.select_related("user")
        .only("text", "datetime", "status", "user__language_code")
        .filter(
            datetime__lte=timezone.now(),
            status__in=(
                Reminder.Status.ACTIVE,
                Reminder.Status.INACTIVE,
                Reminder.Status.REDACTING,
            ),
        )
    )
    for reminder in reminders:
        match reminder.status:
            case Reminder.Status.ACTIVE:
                reminder.status = Reminder.Status.DONE
                reply_message = reminder.text
            case _:
                reminder.status = Reminder.Status.EXPIRED
                reply_message = Phrase.Reminder.EXPIRED + f":\n{reminder.text}"
        with translation.override(reminder.user.language_code):
            bot.send_message(reminder.user.id, str(reply_message))
    Reminder.objects.bulk_update(reminders, ["status"], batch_size=100)
