import os

import telebot

bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))

bot.remove_webhook()
bot.set_webhook("https://d5dogtbmo276i8mgmg42.apigw.yandexcloud.net")
