from django.core.management.base import BaseCommand
from django.utils import timezone, translation, dateparse
from django.template.loader import render_to_string

from api.models import *
from telegram_bot.actions import *
from telegram_bot.generic_actions import city_api_request, timezone_api_request
from telegram_bot.values import Phrase

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from dateparser.search import search_dates

from zoneinfo import ZoneInfo

import telebot


class Command(BaseCommand):
    help = "the main module of the telegram bot"

    def handle(self, *args, **options):
        pass


bot = telebot.TeleBot(settings.TELEBOT_TOKEN)


@bot.message_handler(commands=["start"])
def handle_start(message):
    inc_data = message.__dict__
    inc_user_data = inc_data["json"]["from"]
    inc_user_id = inc_user_data["id"]

    db_user_data = retrieve_user(inc_user_id)

    if db_user_data:
        with translation.override(db_user_data["language_code"]):
            match db_user_data["step"]:
                case User.Step.UPDATE_CITY:
                    reply_message = Phrase.get("Start", "INVALID_CALL")
                case _:
                    user_request_data = {"step": User.Step.CREATE_REMINDER}
                    update_user(inc_user_id, user_request_data)

                    reply_message = Phrase.get("Start", "VALID_CALL") + "\U0001F643"
        bot.send_message(inc_user_id, reply_message)
    else:
        if not translation.check_for_language(inc_user_data["language_code"]):
            inc_user_data["language_code"] = translation.get_language()

        create_user(inc_user_data)
        handle_city(message)


@bot.message_handler(commands=["language"])
def handle_language(message):
    user_id = message.chat.id
    db_user_data = retrieve_user(user_id)

    with translation.override(db_user_data["language_code"]):
        btn1_text = Phrase.get("Button", "EN") + "\U0001F1FA\U0001F1F8"
        btn2_text = Phrase.get("Button", "RU") + "\U0001F1F7\U0001F1FA"

        reply_message = Phrase.get("Language", "INSTRUCTION")

    btn1 = InlineKeyboardButton(btn1_text, callback_data="LANGUAGE:EN:")
    btn2 = InlineKeyboardButton(btn2_text, callback_data="LANGUAGE:RU:")
    reply_markup = InlineKeyboardMarkup()
    reply_markup.add(*(btn1, btn2))

    bot.send_message(message.chat.id, reply_message, reply_markup=reply_markup)


@bot.message_handler(commands=["city"])
def handle_city(message):
    user_id = message.chat.id

    user_request_data = {"step": User.Step.UPDATE_CITY}
    db_user_data = update_user(user_id, user_request_data)

    with translation.override(db_user_data["language_code"]):
        reply_message = Phrase.get("City", "INSTRUCTION")
    bot.send_message(user_id, reply_message)


@bot.message_handler(commands=["reminders"])
def handle_reminders(message):
    user_id = message.chat.id

    db_user_data = retrieve_user(user_id)

    with translation.override(db_user_data["language_code"]):
        user_reminders = get_personal_reminders(user_id)
        if user_reminders:
            context = {
                "header": Phrase.get("Reminders", "HEADER"),
                "user_reminders": user_reminders,
                "instruction": Phrase.get("Reminders", "INSTRUCTION"),
            }

            buttons = (
                InlineKeyboardButton(count, callback_data=f"REMINDER:SELECT:{reminder['id']}")
                for count, reminder in enumerate(user_reminders, start=1)
            )
            reply_markup = InlineKeyboardMarkup()
            reply_markup.add(*buttons)

            reply_message = render_to_string("telegram_bot/Reminders.html", context)
            bot.send_message(user_id, reply_message, parse_mode="HTML", reply_markup=reply_markup)
        else:
            reply_message = Phrase.get("Reminders", "NO_REMINDERS") + "\U0001F610"
            bot.send_message(user_id, reply_message)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    prefix, action, pk = call.data.split(":")

    user_id = call.message.chat.id
    db_user_data = retrieve_user(user_id)

    with translation.override(db_user_data["language_code"]):
        match prefix:
            case "LANGUAGE":
                if translation.get_language() != action.lower():
                    user_request_data = {"language_code": action.lower()}
                    update_user(user_id, user_request_data)

                    translation.activate(action.lower())
                    reply_message = Phrase.get("Language", "ANOTHER_CHOICE")
                else:
                    reply_message = Phrase.get("Language", "SAME_CHOICE")
            case "REMINDER":
                match action:
                    case "SELECT":
                        reminder = retrieve_reminder(pk)
                        if reminder:
                            db_city_data = retrieve_city(db_user_data["city"])
                            inc_timezone_data = timezone_api_request(
                                db_city_data["lat"], db_city_data["lon"]
                            )
                            if inc_timezone_data and isinstance(inc_timezone_data, dict):
                                reminder["datetime"] = dateparse.parse_datetime(
                                    reminder["datetime"]
                                )

                                context = {
                                    "header": Phrase.get("Reminder", "HEADER"),
                                    "reminder": reminder,
                                    "datetime": Phrase.get("Reminder", "DATETIME"),
                                    "status": Phrase.get("Reminder", "STATUS"),
                                }

                                timezone_name = inc_timezone_data["timeZone"]
                                timezone_obj = ZoneInfo(timezone_name)

                                with timezone.override(timezone_obj):
                                    reply_message = render_to_string(
                                        "telegram_bot/Reminder.html", context
                                    )

                        else:
                            reply_message = Phrase.get("Reminder", "NO_REMINDER") + "\U0001F928"
    bot.edit_message_text(reply_message, user_id, call.message.id, parse_mode="HTML")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_id = message.chat.id

    db_user_data = retrieve_user(user_id)

    with translation.override(db_user_data["language_code"]):
        match db_user_data["step"]:
            case User.Step.UPDATE_CITY:
                inc_city_list = city_api_request(message.text)
                if isinstance(inc_city_list, list):
                    if inc_city_list:
                        inc_city_data = inc_city_list[0]
                        inc_city_id = inc_city_data["place_id"]
                        if inc_city_id != db_user_data["city"]:
                            if not retrieve_city(inc_city_id):
                                city_request_data = {
                                    "id": inc_city_id,
                                    "name": inc_city_data["display_name"].split(",")[0],
                                    "lat": inc_city_data["lat"],
                                    "lon": inc_city_data["lon"],
                                }
                                create_city(city_request_data)
                            user_request_data = {
                                "step": User.Step.CREATE_REMINDER,
                                "city": inc_city_id,
                            }
                            update_user(user_id, user_request_data)

                            reply_message = Phrase.get("City", "VALID_RESP")
                        else:
                            reply_message = Phrase.get("City", "SAME_CITY")
                    else:
                        reply_message = Phrase.get("City", "INVALID_CITY")
                else:
                    reply_message = Phrase.get("City", "INVALID_RESP")
            case User.Step.CREATE_REMINDER:
                db_city_data = retrieve_city(db_user_data["city"])
                inc_timezone_data = timezone_api_request(db_city_data["lat"], db_city_data["lon"])
                if inc_timezone_data and isinstance(inc_timezone_data, dict):
                    timezone_name = inc_timezone_data["timeZone"]
                    setup = {
                        "TIMEZONE": timezone_name,
                        "RETURN_AS_TIMEZONE_AWARE": True,
                    }
                    dates = search_dates(message.text, settings=setup)

                    if dates:
                        if len(dates) == 1:
                            datetime_string, datetime_obj = dates[0]
                            if datetime_obj > timezone.now():
                                reminder_request_data = {
                                    "text": message.text.replace(datetime_string, ""),
                                    "datetime": datetime_obj,
                                    "status": Reminder.Status.ACTIVE,
                                    "user": user_id,
                                }
                                create_reminder(reminder_request_data)

                                reply_message = Phrase.get("CreateReminder", "VALID_REMINDER") + "\U00002705"
                            else:
                                reply_message = Phrase.get("CreateReminder", "PAST_DATETIME")
                        else:
                            reply_message = Phrase.get("CreateReminder", "SEVERAL_DATES")
                    else:
                        reply_message = Phrase.get("CreateReminder", "INVALID_REMINDER")
                else:
                    reply_message = Phrase.get("CreateReminder", "INVALID_RESP")
            case User.Step.ADD_DATETIME:
                pass
            case User.Step.UPDATE_DATETIME:
                pass
            case User.Step.UPDATE_TEXT:
                pass
    bot.send_message(user_id, reply_message)


bot.infinity_polling()
