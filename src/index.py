"""
Simple echo Telegram Bot example on Aiogram framework using
Yandex.Cloud functions.
"""

import json
import logging
import os
from aiogram import Bot, Dispatcher, types
from src.telegram_bot.bot import dp

# Logger initialization and logging level setting
log = logging.getLogger(__name__)
log.setLevel(os.environ.get('LOGGING_LEVEL', 'INFO').upper())

async def process_event(event, dp: Dispatcher):
    """
    Converting an Yandex.Cloud functions event to an update and
    handling tha update.
    """

    update = json.loads(event['body'])
    Bot.set_current(dp.bot)
    log.debug('Update: ' + str(update))
    update = types.Update.to_object(update)
    await dp.process_update(update)


async def handler(event, context):
    """Yandex.Cloud functions handler."""

    if event['httpMethod'] == 'POST':
        await process_event(event, dp)

        return {'statusCode': 200, 'body': 'ok'}
    return {'statusCode': 405}