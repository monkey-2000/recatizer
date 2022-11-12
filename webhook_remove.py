import telebot

bot = telebot.TeleBot("5725782396:AAHCjlA4YKa0YlPudMBRNsWI1nEtEOClI5w")

bot.remove_webhook()
bot.set_webhook("https://d5dogtbmo276i8mgmg42.apigw.yandexcloud.net")