from django.core.management.base import BaseCommand
from django.conf import settings
from django.urls import reverse
from django.utils import timezone, translation

from api.models import *
from telegram_bot.timezone import get_city, get_timezone
from telegram_bot.values import Phrase

import telebot
import dateparser
import requests


class Command(BaseCommand):
    help = "the main module of the telegram bot"

    def handle(self, *args, **options):
        pass


BASE_URL = settings.BASE_URL

bot = telebot.TeleBot(settings.TELEBOT_TOKEN)


def dispatch(http_method_name: str, view_name: str, data: dict = None, args: tuple = None) -> dict:
    path = reverse(view_name, args=args)
    url = BASE_URL + path

    handler = getattr(requests, http_method_name)
    return handler(url, data=data).json()


def get_available_language_codes():
    return map(str.lower, filter(lambda x: not x.startswith("__"), dir(Phrase.Button)))


@bot.message_handler(commands=["start"])
def handle_start(message):
    incoming_data = message.__dict__
    incoming_user_data = incoming_data["json"]["from"]
    language_code = incoming_user_data["language_code"]

    translation.activate(language_code)

    db_user_data = dispatch("get", "user-detail", args=(incoming_user_data["id"],))
    user_step = db_user_data.get("step", None)

    match user_step:
        case None:
            dispatch("post", "user-list", data=incoming_user_data)
            handle_city(message)
        case User.Step.UPDATE_CITY:
            reply_message = Phrase.get("Start", "INVALID_CALL")
            bot.send_message(incoming_user_data["id"], reply_message)
        case _:
            user_request_data = {"step": User.Step.CREATE_REMINDER}
            dispatch("patch", "user-detail", data=user_request_data, args=(incoming_user_data["id"],))

            reply_message = Phrase.get("Start", "VALID_CALL")
            bot.send_message(incoming_user_data["id"], reply_message)
    translation.deactivate()


@bot.message_handler(commands=["language"])
def handle_language(message):
    user_id = message.chat.id
    db_user_data = dispatch("get", "user-detail", args=(user_id,))
    language_code = db_user_data["language_code"]

    translation.activate(language_code)

    btn1_name = Phrase.get("Button", "EN")
    btn2_name = Phrase.get("Button", "RU")

    btn1_callback = "LANGUAGE:EN"
    btn2_callback = "LANGUAGE:RU"

    btn1 = telebot.types.InlineKeyboardButton(btn1_name, callback_data=btn1_callback)
    btn2 = telebot.types.InlineKeyboardButton(btn2_name, callback_data=btn2_callback)
    reply_markup = telebot.types.InlineKeyboardMarkup()
    reply_markup.add(*(btn1, btn2))

    reply_message = Phrase.get("Language", "INSTRUCTION")
    bot.send_message(message.chat.id, reply_message, reply_markup=reply_markup)

    translation.deactivate()


@bot.message_handler(commands=["city"])
def handle_city(message):
    user_id = message.chat.id
    db_user_data = dispatch("get", "user-detail", args=(user_id,))
    language_code = db_user_data["language_code"]

    user_request_data = {"step": User.Step.UPDATE_CITY}

    if language_code not in get_available_language_codes():
        user_request_data["language_code"] = "en"
    else:
        translation.activate(language_code)

    dispatch("patch", "user-detail", data=user_request_data, args=(user_id,))

    reply_message = Phrase.get("City", "INSTRUCTION")
    bot.send_message(user_id, reply_message)

    translation.deactivate()


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    prefix, action = call.data.split(":")

    user_id = call.message.chat.id
    db_user_data = dispatch("get", "user-detail", args=(user_id,))
    language_code = db_user_data["language_code"]

    translation.activate(language_code)

    match prefix:
        case "LANGUAGE":
            if language_code != action.lower():
                user_request_data = {"language_code": action.lower()}
                dispatch("patch", "user-detail", data=user_request_data, args=(user_id,))

                translation.activate(action.lower())
                reply_message = Phrase.get("Language", "ANOTHER_CHOICE")
            else:
                reply_message = Phrase.get("Language", "SAME_CHOICE")
            bot.send_message(user_id, reply_message)

    translation.deactivate()


@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_id = message.chat.id
    db_user_data = dispatch("get", "user-detail", args=(user_id,))
    user_step = db_user_data["step"]

    language_code = db_user_data["language_code"]
    translation.activate(language_code)

    match user_step:
        case User.Step.UPDATE_CITY:
            resp = get_city(city=message.text, format="json", limit=1)
            if isinstance(resp, bool) or not resp.ok:
                reply_message = Phrase.get("City", "INVALID_RESP")
            elif info_list := resp.json():
                city_info = info_list[0]

                db_city_data = dispatch("get", "city-detail", args=(city_info["place_id"],))
                city_id = db_city_data.get("id", None)

                if not city_id:
                    city_request_data = {
                        "id": city_info["place_id"],
                        "name": city_info["display_name"].split(",")[0],
                        "lat": city_info["lat"],
                        "lon": city_info["lon"]
                    }
                    dispatch("post", "city-list", data=city_request_data)

                user_request_data = {"step": User.Step.CREATE_REMINDER, "city": city_info["place_id"]}
                dispatch("patch", "user-detail", data=user_request_data, args=(user_id,))

                reply_message = Phrase.get("City", "VALID_RESP")
            else:
                reply_message = Phrase.get("City", "INVALID_CITY")
            bot.send_message(user_id, reply_message)
        case User.Step.CREATE_REMINDER:
            reminder_content = message.text.split("\n")
            if len(reminder_content) == 2:
                text, datetime = reminder_content

                db_city_data = dispatch("get", "city-detail", args=(db_user_data["city"],))
                resp = get_timezone(latitude=db_city_data["lat"], longitude=db_city_data["lon"])

                if isinstance(resp, bool) or not resp.ok:
                    reply_message = Phrase.get("City", "INVALID_RESP")
                else:
                    tz_name = resp.json()["timeZone"]
                    setup = {'TIMEZONE': tz_name, 'RETURN_AS_TIMEZONE_AWARE': True}
                    datetime_obj = dateparser.parse(datetime, settings=setup)

                    if datetime_obj:
                        if datetime_obj > timezone.now():
                            reminder_request_data = {
                                "text": text,
                                "datetime": datetime_obj,
                                "status": Reminder.Status.ACTIVE,
                                "user": user_id
                            }
                            print(reminder_request_data)
                            print(type(datetime_obj))
                            dispatch("post", "reminder-list", data=reminder_request_data)

                            reply_message = Phrase.get("CreateReminder", "VALID_DATETIME")
                        else:
                            reply_message = Phrase.get("CreateReminder", "PAST_DATETIME")
                    else:
                        reply_message = Phrase.get("CreateReminder", "INVALID_RESP")
            else:
                reply_message = Phrase.get("CreateReminder", "WRONG_REMINDER_FORMAT")
            bot.send_message(user_id, reply_message)
        case User.Step.ADD_DATETIME:
            pass
        case User.Step.UPDATE_DATETIME:
            pass
        case User.Step.UPDATE_TEXT:
            pass
    translation.deactivate()


bot.infinity_polling()
