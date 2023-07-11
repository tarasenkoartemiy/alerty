from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from telebot import types
from .handlers import bot


class BotAPIView(APIView):
    def post(self, request, *args, **kwargs):
        json_str = request.body.decode('UTF-8')
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])

        return Response(status=status.HTTP_200_OK)
