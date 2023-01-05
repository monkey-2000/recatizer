import os

import telebot
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))

bot.remove_webhook()
bot.set_webhook("https://d5df50sg46l7rq5su4dl.apigw.yandexcloud.net")
# bot.set_webhook("https://d5dogtbmo276i8mgmg42.apigw.yandexcloud.net")
