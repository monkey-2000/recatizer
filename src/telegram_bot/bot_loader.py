import asyncio
import os
import uuid
from time import sleep, time

import aiohttp
import cv2
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputFile
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData

import mercantile
# from aiogram.utils import emoji
# from telegram import Bot, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, \
#     InlineKeyboardMarkup, InputMediaDocument
# from json import dumps
# #
# from telegram.utils import types
from dotenv import load_dotenv

from src.configs.service_config import default_service_config
from src.entities.cat import ClosestCats, Cat
from src.entities.person import Person
from src.telegram_bot.bot_tools.find_cat_handler import get_find_menu_kb


from src.telegram_bot.configs.bot_base_configs import S3ClientConfig
from src.utils.s3_client import YandexS3Client



class DataUploader:

    MatchesCb = CallbackData("matches", "action", "match_id")
    def __init__(self, token, s3_config: S3ClientConfig, image_dir='/tmp'):
        self.bot = Bot(token)
        self.s3_client = YandexS3Client(
            s3_config.aws_access_key_id, s3_config.aws_secret_access_key
        )
        self.token=token
        self.image_dir=image_dir



    async def _send_match(self, chat_id, match_id, cat):



            os.makedirs(self.image_dir, exist_ok=True)
            media_group = types.MediaGroup()
            for path in cat.paths:

                cat_image = self.s3_client.load_image(path)
                cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
                # cat_image = cv2.imencode(".jpg", cat_image)[1].tobytes()
                image_name = "{0}.jpg".format(str(uuid.uuid4()))
                image_path = os.path.join(self.image_dir, image_name)
                cv2.imwrite(image_path, cat_image)
                media_group.attach_photo(InputMediaPhoto(media=InputFile(image_path) ))
                # TODO resize photo

            os.remove(image_path)
            if cat.quadkey != "no_quad":
                    titlat = mercantile.quadkey_to_tile(cat.quadkey)
                    coo = mercantile.ul(titlat)
                    await self.bot.send_location(chat_id=chat_id, latitude=coo.lat, longitude=coo.lng)
            await self.bot.send_media_group(chat_id=chat_id, media=media_group)
            await  self.bot.send_message(
                chat_id=chat_id, text=cat.additional_info, reply_markup=self.get_match_kb(match_id))




    async def _send_matches(self, cats, chat_id, match_ids):
        # bot = Bot(token=self.token)

        try:
            await self.bot.send_message(chat_id=chat_id,
                                        text="\U0001F638\U0001F638\U0001F638\n YEEAAAH, New matches for you!!!")
            for match_id, cat in zip(match_ids, cats):

                await self._send_match(cat=cat, match_id=match_id, chat_id=chat_id)

        finally:
            await self.bot.send_message(chat_id=chat_id,
                                        text="That is all new matches.\n \U0001F638\U0001F638\U0001F638",
                                        reply_markup=get_find_menu_kb())
            await (await self.bot.get_session()).close()


    def upload(self, closest: ClosestCats):
        asyncio.run(self._send_matches(cats=closest.cats,
                                        chat_id=closest.person.chat_id,
                                       match_ids=closest.match_ids))

    def _upload(self, cats: list, chat_id: int):
        asyncio.run(self._send_matches(cats=cats,
                                       chat_id=chat_id))

    def get_match_kb(self, match_id):
        buttons = [
            types.InlineKeyboardButton(
                text="\U0000274c", callback_data=self.MatchesCb.new(action="no", match_id=match_id)
            ),
            types.InlineKeyboardButton(
                text="My \U0001F638", callback_data=self.MatchesCb.new(action="yes", match_id=match_id)
            ),

        ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        return keyboard



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
    load_dotenv()

    bot_loader = DataUploader(
        default_service_config.bot_token,
        default_service_config.s3_client_config,
        image_dir = os.environ.get("PROJECT_DIR") + "/tmp"
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

    cat2 = Cat(
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
        cats=[cat1, cat2],
        distances = [1.0])

    # bot_loader.upload_one(cl)
    bot_loader.upload(cl)


