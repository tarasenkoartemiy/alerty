from django.conf import settings
from django.utils import translation, timezone
from dateparser.search import search_dates
from requests import get
from .models import City, User, Reminder
from .values import Phrase
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import telebot

bot = telebot.TeleBot(settings.BOT_TOKEN)


@bot.message_handler(commands=["start"])
def handle_start(message):
    inc_data = message.__dict__
    inc_user_data = inc_data["json"]["from"]
    queryset = User.objects.filter(id=inc_user_data["id"])
    if queryset:
        user = queryset.get()
        if user.city:
            user.step = User.Step.CREATE_REMINDER
            user.save()
            reply_message = Phrase.Start.VALID_CALL
        else:
            reply_message = Phrase.Start.INVALID_CALL
        with translation.override(user.language_code):
            bot.send_message(user.id, str(reply_message))
    else:
        if not translation.check_for_language(inc_user_data["language_code"]):
            inc_user_data["language_code"] = translation.get_language()
        User.objects.create(**inc_user_data)
        handle_city(message)


@bot.message_handler(commands=["city"])
def handle_city(message):
    user = User.objects.get(id=message.chat.id)
    user.step = User.Step.UPDATE_CITY
    user.save()
    with translation.override(user.language_code):
        bot.send_message(user.id, str(Phrase.City.INSTRUCTION))


@bot.message_handler(commands=["language"])
def handle_language(message):
    user = User.objects.get(id=message.chat.id)
    en_btn = InlineKeyboardButton("\U0001F1FA\U0001F1F8", callback_data="LANGUAGE:EN:")
    ru_btn = InlineKeyboardButton("\U0001F1F7\U0001F1FA", callback_data="LANGUAGE:RU:")
    reply_markup = InlineKeyboardMarkup().add(en_btn, ru_btn)
    with translation.override(user.language_code):
        bot.send_message(user.id, str(Phrase.Language.INSTRUCTION), reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    prefix, action, pk = call.data.split(":")
    user = User.objects.get(id=call.message.chat.id)

    match prefix:
        case "LANGUAGE":
            if user.language_code != action.lower():
                user.language_code = action.lower()
                user.save()
                reply_message = Phrase.Language.ANOTHER_CHOICE
            else:
                reply_message = Phrase.Language.SAME_CHOICE
        case "REMINDER":
            pass
    with translation.override(user.language_code):
        bot.edit_message_text(str(reply_message), user.id, call.message.id)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    user = User.objects.select_related("city").get(id=message.chat.id)
    match user.step:
        case User.Step.UPDATE_CITY:
            params = {"city": message.text, "format": "json", "limit": 1}
            headers = {"accept-language": "en-US,en;q=0.9"}
            nominatim_resp = get("https://nominatim.openstreetmap.org/search?", params, headers=headers)
            inc_city_list = decode_json(nominatim_resp)
            if isinstance(inc_city_list, list):
                if inc_city_list:
                    inc_city_data = inc_city_list[0]
                    inc_city_id = inc_city_data["place_id"]
                    if user.city and user.city.id != inc_city_id or not user.city:
                        city, created = City.objects.get_or_create(
                            id=inc_city_id,
                            name=inc_city_data["display_name"].split(",")[0],
                            lat=inc_city_data["lat"],
                            lon=inc_city_data["lon"]
                        )
                        user.step = User.Step.CREATE_REMINDER
                        user.city = city
                        user.save()
                        reply_message = Phrase.City.VALID_RESP
                    else:
                        reply_message = Phrase.City.SAME_CITY
                else:
                    reply_message = Phrase.City.INVALID_CITY
            else:
                reply_message = Phrase.City.INVALID_RESP
        case User.Step.CREATE_REMINDER:
            params = {"latitude": user.city.lat, "longitude": user.city.lon}
            timeapi_resp = get("https://timeapi.io/api/Time/current/coordinate?", params)
            inc_timezone_data = decode_json(timeapi_resp)
            if inc_timezone_data and isinstance(inc_timezone_data, dict):
                setup = {
                    "TIMEZONE": inc_timezone_data["timeZone"],
                    "RETURN_AS_TIMEZONE_AWARE": True,
                }
                dates = search_dates(message.text, settings=setup)
                if dates:
                    if len(dates) == 1:
                        datetime_string, datetime_obj = dates[0]
                        if datetime_obj > timezone.now():
                            Reminder.objects.create(
                                text=message.text.replace(datetime_string, ""),
                                datetime=datetime_obj,
                                status=Reminder.Status.ACTIVE,
                                user=user
                            )
                            reply_message = Phrase.CreateReminder.VALID_REMINDER + "\U00002705"
                        else:
                            reply_message = Phrase.CreateReminder.PAST_DATETIME
                    else:
                        reply_message = Phrase.CreateReminder.SEVERAL_DATES
                else:
                    reply_message = Phrase.CreateReminder.INVALID_REMINDER
            else:
                reply_message = Phrase.CreateReminder.INVALID_RESP
        case User.Step.ADD_DATETIME:
            pass
        case User.Step.UPDATE_DATETIME:
            pass
        case User.Step.UPDATE_TEXT:
            pass
    with translation.override(user.language_code):
        bot.send_message(user.id, str(reply_message))


def decode_json(response):
    if response.ok and response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
