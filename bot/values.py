from django.utils.translation import gettext_lazy as _


class Phrase:
    class Start:
        VALID_CALL = _("What should I remind you about?")
        INVALID_CALL = _("You can't use this command yet")

    class City:
        INSTRUCTION = _("Please write the name of the city whose time zone you want to use")
        VALID_RESP = _("Your time zone has been successfully determined")
        INVALID_RESP = _("The service I'm using for this operation is not working right now")
        INVALID_CITY = _("I don't know this city, try again")
        SAME_CITY = _("You are already using the time zone of this city")

    class Language:
        INSTRUCTION = _("Please select interface language")
        SAME_CHOICE = _("This language has already been chosen by you")
        ANOTHER_CHOICE = _("Your language has been successfully changed")

    class Reminder:
        HEADER = _("Reminder")
        DATETIME = _("Dispatch time")
        STATUS = _("Status")
        NO_REMINDER = _("Reminder not found")

    class Reminders:
        HEADER = _("My reminders")
        INSTRUCTION = _("Select number to edit")
        NO_REMINDERS = _("You have no reminders")

    class CreateReminder:
        INVALID_RESP = _("I can't determine what time zone you are in right now. Please try again later")
        VALID_REMINDER = _("Reminder successfully recorded")
        PAST_DATETIME = _("You cannot select a date that has already passed")
        INVALID_REMINDER = _("I can't recognize the datetime in your reminder")
        SEVERAL_DATES = _("I found several datetime indications in your reminder, please indicate only one")