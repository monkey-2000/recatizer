import telebot
from bot import dp


def handler(event, _):
    message = telebot.types.Update.de_json(event['body'])
    dp.process_new_updates([message])
    return {
        'statusCode': 200,
        'body': '!',
    }