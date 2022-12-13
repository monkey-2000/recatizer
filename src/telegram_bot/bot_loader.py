from time import sleep

import cv2
from telegram import Bot, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from json import dumps
from src.entities.cat import ClosestCats
from src.telegram_bot.configs.bot_base_configs import S3ClientConfig
from src.utils.s3_client import YandexS3Client


class DataUploader:
    def __init__(self, token, s3_config: S3ClientConfig):
        self.bot = Bot(token)
        self.s3_client = YandexS3Client(
            s3_config.aws_access_key_id, s3_config.aws_secret_access_key
        )

    def match_notify(self, closest: ClosestCats):
        closest_cats_amount = len(closest.cats)
        if closest_cats_amount == 1:
            comment = (
                "Good news! Your cat {0} have {1} match. "
                "Go to the \my_matches and get contact information "
                "if your cat is among the matches ".format(
                    closest.person._id, closest_cats_amount
                )
            )
        else:
            comment = (
                "Good news! Your cat {0} have {1} matches. "
                "Go to the \my_matches and get contact information "
                "if your cat is among the matches ".format(
                    closest.person._id, closest_cats_amount
                )
            )
        cat_image = self.s3_client.load_image(closest.person.paths[0])
        cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
        cat_image_bytes = cv2.imencode(".jpg", cat_image)[1].tobytes()

        self.bot.send_photo(
            closest.person.chat_id, photo=cat_image_bytes, caption=comment
        )

    def upload(self, closest: ClosestCats):

        closest_cats_amount = len(closest.cats)

        for cat_num, cat in enumerate(closest.cats):

            media_group = []
            for path in cat.paths:

                cat_image = self.s3_client.load_image(path)
                cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
                cat_image_bytes = cv2.imencode(".jpg", cat_image)[1].tobytes()
                media_group.append(InputMediaPhoto(media=cat_image_bytes))

            self.bot.send_message(
                chat_id=closest.person.chat_id,
                text="-------cat {}-------".format(cat._id),
            )
            self.bot.send_media_group(chat_id=closest.person.chat_id, media=media_group)
            self.bot.send_message(
                chat_id=closest.person.chat_id, text=cat.additional_info
            )

            self.bot.send_message(
                chat_id=closest.person.chat_id, text="--------------------"
            )
