from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone, translation

from api.models import *
from telegram_bot.actions import *
from telegram_bot.generic_actions import city_api_request
from telegram_bot.values import Phrase

import telebot
import dateparser


class Command(BaseCommand):
    help = "the main module of the telegram bot"

    def handle(self, *args, **options):
        pass


TIMEAPI_LINK = "https://timeapi.io/api/TimeZone/coordinate?"

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

                    reply_message = Phrase.get("Start", "INVALID_CALL")
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

    user_request_data = {"step": User.Step.UPDATE_CITY}
    db_user_data = update_user(user_id, user_request_data)

    with translation.override(db_user_data["language_code"]):
        reply_message = Phrase.get("City", "INSTRUCTION")
        bot.send_message(user_id, reply_message)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    prefix, action = call.data.split(":")

    user_id = call.message.chat.id
    db_user_data = retrieve_user(user_id)
    language_code = db_user_data["language_code"]

    translation.activate(language_code)

    match prefix:
        case "LANGUAGE":
            if language_code != action.lower():
                user_request_data = {"language_code": action.lower()}
                update_user(user_id, user_request_data)

                translation.activate(action.lower())
                reply_message = Phrase.get("Language", "ANOTHER_CHOICE")
            else:
                reply_message = Phrase.get("Language", "SAME_CHOICE")
            bot.send_message(user_id, reply_message)

    translation.deactivate()


@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_id = message.chat.id

    db_user_data = retrieve_user(user_id)

    with translation.override(db_user_data["language_code"]):
        match db_user_data["step"]:
            case User.Step.UPDATE_CITY:
                response = city_api_request(message.text)
                if response.ok and response.headers.get("Content-Type", "").startswith("application/json"):
                    inc_city_data = response.json()
                    if inc_city_data:
                        inc_city_id = inc_city_data["place_id"]
                        if inc_city_id != db_user_data["city"]:
                            if not retrieve_city(inc_city_id):
                                city_request_data = {
                                    "id": inc_city_id,
                                    "name": inc_city_data["display_name"].split(",")[0],
                                    "lat": inc_city_data["lat"],
                                    "lot": inc_city_data["lot"]
                                }
                                create_city(city_request_data)
                            user_request_data = {"step": User.Step.CREATE_REMINDER, "city": inc_city_id}
                            update_user(user_id, user_request_data)

                            reply_message = Phrase.get("City", "VALID_RESP")
                        else:
                            reply_message = "Совпадает город сука"
                    else:
                        reply_message = Phrase.get("City", "INVALID_CITY")
                else:
                    reply_message = Phrase.get("City", "INVALID_RESP")
                bot.send_message(user_id, reply_message)
            case User.Step.CREATE_REMINDER:
                # reminder_content = message.text.split("\n")
                # if len(reminder_content) == 2:
                #     text, datetime = reminder_content
                #
                #     db_city_data = dispatch("get", "city-detail", args=(db_user_data["city"],))
                #     resp = get_timezone(latitude=db_city_data["lat"], longitude=db_city_data["lon"])
                #
                #     if isinstance(resp, bool) or not resp.ok:
                #         reply_message = Phrase.get("City", "INVALID_RESP")
                #     else:
                #         tz_name = resp.json()["timeZone"]
                #         setup = {'TIMEZONE': tz_name, 'RETURN_AS_TIMEZONE_AWARE': True}
                #         datetime_obj = dateparser.parse(datetime, settings=setup)
                #
                #         if datetime_obj:
                #             if datetime_obj > timezone.now():
                #                 reminder_request_data = {
                #                     "text": text,
                #                     "datetime": datetime_obj,
                #                     "status": Reminder.Status.ACTIVE,
                #                     "user": user_id
                #                 }
                #                 print(reminder_request_data)
                #                 print(type(datetime_obj))
                #                 dispatch("post", "reminder-list", data=reminder_request_data)
                #
                #                 reply_message = Phrase.get("CreateReminder", "VALID_DATETIME")
                #             else:
                #                 reply_message = Phrase.get("CreateReminder", "PAST_DATETIME")
                #         else:
                #             reply_message = Phrase.get("CreateReminder", "INVALID_RESP")
                # else:
                #     reply_message = Phrase.get("CreateReminder", "WRONG_REMINDER_FORMAT")
                # bot.send_message(user_id, reply_message)
                pass
            case User.Step.ADD_DATETIME:
                pass
            case User.Step.UPDATE_DATETIME:
                pass
            case User.Step.UPDATE_TEXT:
                pass


bot.infinity_polling()
