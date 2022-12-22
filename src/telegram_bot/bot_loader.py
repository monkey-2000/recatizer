import asyncio
from time import sleep, time

import cv2
# from aiogram import Bot, types, Dispatcher
# from aiogram.types import InputMediaPhoto, InputMediaDocument
# from aiogram.utils import executor
# from aiogram.utils.callback_data import CallbackData

import mercantile
from aiogram.utils import emoji
from telegram import Bot, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, \
    InlineKeyboardMarkup, InputMediaDocument
from json import dumps
#
from telegram.utils import types

from src.configs.service_config import default_service_config
from src.entities.cat import ClosestCats, Cat
from src.entities.person import Person

from src.telegram_bot.configs.bot_base_configs import S3ClientConfig
from src.utils.s3_client import YandexS3Client



class DataUploader:

    # MatchesCb = CallbackData("matches", "action", "cat_id")
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

    def upload_one(self, closest: ClosestCats):
        keyboard = ReplyKeyboardMarkup([[KeyboardButton("/not_may_cat"), KeyboardButton("/mycat")], ["/start", "/I_found_my_cat"]],
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("\U0000274c"), KeyboardButton("\U0000274c")], ["\U00002b05", "/I_found_my_cat"]],
            one_time_keyboard=True,
            resize_keyboard=True)


        media_group = []
        cat = closest.cats[0]
        for path in cat.paths:
            cat_image = self.s3_client.load_image(path)
            cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
            cat_image_bytes = cv2.imencode(".jpg", cat_image)[1].tobytes()
            media_group.append(InputMediaPhoto(media=cat_image_bytes))
        if cat.quadkey != "no_quad":
            titlat = mercantile.quadkey_to_tile(cat.quadkey)
            coo = mercantile.ul(titlat)
            self.bot.send_location(chat_id=closest.person.chat_id, latitude=coo.lat, longitude=coo.lng)
        self.bot.send_media_group(chat_id=closest.person.chat_id, media=media_group)
        self.bot.send_message(
            chat_id=closest.person.chat_id, text=cat.additional_info, reply_markup=keyboard
        )


    # async def _send_match(self, chat_id, cat):
    #         buttons = [
    #             types.InlineKeyboardButton(
    #                 text="MyCat", callback_data=self.MatchesCb.new(action="yes", cat_id="1")
    #             ),
    #             types.InlineKeyboardButton(
    #                 text="NotMyCat", callback_data=self.MatchesCb.new(action="no", cat_id="1")
    #             )
    #         ]
    #         keyboard = types.InlineKeyboardMarkup(row_width=1)
    #         keyboard.add(*buttons)
    #
    #         media_group = []
    #         for path in cat.paths:
    #
    #             cat_image = self.s3_client.load_image(path)
    #             cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
    #             cat_image_bytes = cv2.imencode(".jpg", cat_image)[1].tobytes()
    #             #media_group.append(InputMediaPhoto(media=cat_image_bytes))
    #             media_group.append(InputMediaDocument(media=cat_image_bytes))
    #
    #         # await self.bot.send_media_group(chat_id=chat_id, media=media_group)
    #         await  self.bot.send_message(
    #             chat_id=chat_id, text=cat.additional_info, reply_markup=keyboard)
    #
    #
    #
    #
    # def upload_in_loop(self, closest: ClosestCats):
    #     # dp = Dispatcher(self.bot, loop= asyncio.get_event_loop())
    #     # for cat in closest.cats:
    #     #     dp.loop.create_task(self._send_match(chat_id=closest.person.chat_id,
    #     #                                          cat=cat))
    #     # # dp.loop.create_task(dp.loop.stop())
    #     # # executor.start_polling(dp)
    #     loop = asyncio.get_event_loop()
    #     try:
    #         loop.run_until_complete(asyncio.wait([self._send_match(chat_id=closest.person.chat_id,
    #                                              cat=closest.cats[0])]))  # передайте точку входа
    #     finally:
    #         # действия на выходе, если требуются
    #         pass



    # def upload(self, closest: ClosestCats):
    #
    #     closest_cats_amount = len(closest.cats)
    #
    #     for cat_num, cat in enumerate(closest.cats):
    #
    #
    #         media_group = []
    #         for path in cat.paths:
    #
    #             cat_image = self.s3_client.load_image(path)
    #             cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
    #             cat_image_bytes = cv2.imencode(".jpg", cat_image)[1].tobytes()
    #             #media_group.append(InputMediaPhoto(media=cat_image_bytes))
    #             media_group.append(InputMediaDocument(media=cat_image_bytes))
    #
    #
    #         self.bot.send_message(
    #             chat_id=closest.person.chat_id,
    #             text="-------cat {}-------".format(cat._id),
    #         )
    #         self.bot.send_media_group(chat_id=closest.person.chat_id, media=media_group)
    #         self.bot.send_message(
    #             chat_id=closest.person.chat_id, text=cat.additional_info, reply_markup=keyboard
    #         )
    #
    #         self.bot.send_message(
    #             chat_id=closest.person.chat_id, text="--------------------"
    #         )


if __name__ == "__main__":
    bot_loader = DataUploader(
        default_service_config.bot_token, default_service_config.s3_client_config
    )
    cat1 = Cat(
            _id=None,
            paths=["users_data/c7c8b97c0e53983d8a0fd3bc2a53222bec4194454adcf3fe145a8dae5b950a19.jpg"],
            quadkey="0313102310",
            embeddings=None,
            is_active=True,
            additional_info="I miss",
            chat_id=450390623,
            person_name="BORRIZ",
            dt=time()
        )
    person = Person( _id=None,
                    paths=["users_data/c7c8b97c0e53983d8a0fd3bc2a53222bec4194454adcf3fe145a8dae5b950a19.jpg"],
                    quadkey="no",
                    embeddings=None,
                    is_active=True,
                    additional_info="no",
                    chat_id=450390623,
                    dt=-float('inf'))
    cl = ClosestCats(
        person = person,
        cats=[cat1],
        distances = [1.0])

    bot_loader.upload_one(cl)

