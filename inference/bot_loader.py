import os
import uuid
from time import sleep

import cv2
from telegram import Bot, InputMediaPhoto
from json import dumps

from inference.entities.cat import ClosestCats
from telegram_bot.configs.bot_base_configs import S3ClientConfig
from telegram_bot.configs.bot_cfgs import bot_config
from telegram_bot.s3_client import YandexS3Client


class DataUploader:
    def __init__(self, token, s3_config: S3ClientConfig):
        self.bot = Bot(token)
        self.s3_client = YandexS3Client(s3_config.aws_access_key_id, s3_config.aws_secret_access_key)

    def upload(self, closest: ClosestCats):
        media_group = []
        for cat in closest.cats:
           # media_group.append(InputMediaPhoto(open(path, "rb"), caption=dumps(cat.additional_info)))
            for path in cat.paths:
                cat_image = self.s3_client.load_image(path)
                cat_image_bytes = cv2.imencode('.jpg', cat_image)[1].tobytes()
                media_group.append(InputMediaPhoto(media=cat_image_bytes))
            self.bot.send_media_group(chat_id=closest.person.chat_id,
                                  media=media_group)
            self.bot.send_message(closest.person.chat_id, cat.additional_info)
            sleep(10)



