from bson import ObjectId
from pymongo import MongoClient
import redis

from src.cats_queue.producer import Producer
from src.services.mongo_service import (
    CatsMongoClient,
    PeopleMongoClient,
    AnswersMongoClient,
)
from src.services.redis_service import CacheClient
from src.telegram_bot.configs.bot_base_configs import TgBotConfig
from src.utils.s3_client import YandexS3Client

import os
import uuid

import cv2
import mercantile
from aiogram import types
from aiogram.types import InputMediaPhoto, InputFile
from aiogram.utils.callback_data import CallbackData


class MatchSender:

    MatchesCb = CallbackData("matches", "action", "match_id")

    def __init__(self, image_dir):
        self.image_dir = image_dir

    async def _send_match(
            self, message, cat, cat_images: list,  more_info=False
    ):

        os.makedirs(self.image_dir, exist_ok=True)
        media_group = types.MediaGroup()
        for cat_image in cat_images:
            image_name = "{0}.jpg".format(str(uuid.uuid4()))
            image_path = os.path.join(self.image_dir, image_name)
            cv2.imwrite(image_path, cat_image)
            media_group.attach_photo(InputMediaPhoto(media=InputFile(image_path)))
            # TODO resize photo

            os.remove(image_path)
        if cat.quadkey != "no_quad":
            titlat = mercantile.quadkey_to_tile(cat.quadkey)
            coo = mercantile.ul(titlat)
            await message.answer_location(latitude=coo.lat, longitude=coo.lng)
        await message.answer_media_group(media=media_group)

        await message.answer(
            text=f"Person {cat.person_name} saw this cat. This is yours?",
            reply_markup=self.get_match_kb(cat._id, more_info=more_info),
        )

    async def send_match(
        self, message, cat, cat_images: list, match_id, more_info=False, additional=None
    ):

        os.makedirs(self.image_dir, exist_ok=True)
        media_group = types.MediaGroup()
        for cat_image in cat_images:
            image_name = "{0}.jpg".format(str(uuid.uuid4()))
            image_path = os.path.join(self.image_dir, image_name)
            cv2.imwrite(image_path, cat_image)
            media_group.attach_photo(InputMediaPhoto(media=InputFile(image_path)))
            # TODO resize photo

            os.remove(image_path)
        if cat.quadkey != "no_quad":
            titlat = mercantile.quadkey_to_tile(cat.quadkey)
            coo = mercantile.ul(titlat)
            await message.answer_location(latitude=coo.lat, longitude=coo.lng)
        await message.answer_media_group(media=media_group)

        await message.answer(
            text=f"Person {cat.person_name} saw this cat. This is yours?",
            reply_markup=self.get_match_kb(match_id, more_info=more_info),
        )

    def get_match_kb(self, match_id, more_info=False):

        buttons = [
            types.InlineKeyboardButton(
                text="\U0000274c",
                callback_data=self.MatchesCb.new(action="no", match_id=match_id),
            ),
            types.InlineKeyboardButton(
                text="\U00002705",
                callback_data=self.MatchesCb.new(action="yes", match_id=match_id),
            ),
        ]

        if more_info:

            buttons.append(
                types.InlineKeyboardButton(
                    text="More",
                    callback_data=self.MatchesCb.new(
                        action="show_more_info", match_id=match_id
                    ),
                )
            )

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        return keyboard


class UserProfileClient:
    def __init__(self, config: TgBotConfig):
        client = MongoClient(config.mongoDB_url)
        self.cats_db = CatsMongoClient(client.main)
        self.people_db = PeopleMongoClient(client.main)
        self.answers_db = AnswersMongoClient(client.main)
        # self.image_dir = config.image_dir
        self.s3_client = YandexS3Client(
            config.s3_client_config.aws_access_key_id,
            config.s3_client_config.aws_secret_access_key,
            local_path="tmp_local_storage"
        )
        self.image_dir = config.image_dir
        self.__sender = MatchSender(self.image_dir)
        self.__kafka_producer = Producer()

        self.redis_client = CacheClient(config.redis_client_config)

    def get_matches(self, chat_id: int):
        """Load last answer from cache"""
        if self.redis_client.exists(chat_id):
            return self.redis_client.get(chat_id)
        else:
            return
            # TODO start new search!!!!!!!!!!!!!!!!!!!
            # Load cat from MongoDB
            # Send to Model

    def exists_match(self, chat_id, cat):
        matches = self.redis_client.get(chat_id)
        return cat in matches

    def delete_match(self, chat_id, cat):
        matches = self.redis_client.get(chat_id)

        matches.remove(cat)
        return self.redis_client.set(chat_id, matches)



    async def _send_match(self, message: types.Message, cat, more_info=False):
        about = None
        if len(cat.paths) > 1 or cat.additional_info != "no info":
            more_info = True
            about = "We have some extra info about this cat:\n"

            if cat.additional_info != "no info":
                about += "-additional info;\n"
            if len(cat.paths) > 1:
                about += "-{0} photos\n".format(len(cat.paths))
            about += "Press More to see it."

        path = cat.paths[0]  # TODO choose best photo
        cat_image = self.s3_client.load_image(path)
        cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)

        await self.__sender._send_match(
            message, cat, [cat_image], more_info=more_info
        )
        if about:
            await message.answer(text=about)





    async def send_match(self, message: types.Message, cat, match_id, more_info=False):
        about = None
        if len(cat.paths) > 1 or cat.additional_info != "no info":
            more_info = True
            about = "We have some extra info about this cat:\n"

            if cat.additional_info != "no info":
                about += "-additional info;\n"
            if len(cat.paths) > 1:
                about += "-{0} photos\n".format(len(cat.paths))
            about += "Press More to see it."

        path = cat.paths[0]  # TODO choose best photo
        cat_image = self.s3_client.load_image(path)
        cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)

        await self.__sender.send_match(
            message, cat, [cat_image], match_id, more_info=more_info
        )
        if about:
            await message.answer(text=about)

    async def send_match_with_extra(self, message: types.Message, match_id: str):
        answer = self.answers_db.find({"_id": ObjectId(match_id)})[0]
        cat = self.cats_db.find({"_id": answer.match_cat_id})[0]
        cat_images = []
        for path in cat.paths:
            cat_image = self.s3_client.load_image(path)
            cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
            cat_images.append(cat_image)

        media_group = types.MediaGroup()
        for cat_image in cat_images:
            image_name = "{0}.jpg".format(str(uuid.uuid4()))
            image_path = os.path.join(self.image_dir, image_name)
            cv2.imwrite(image_path, cat_image)
            media_group.attach_photo(InputMediaPhoto(media=InputFile(image_path)))

        if cat.additional_info != "no info":
            await message.answer(text=f"ADDITIONAL INFO: {cat.additional_info}")

        await self.__sender.send_match(message, cat, cat_images, match_id)

        #

    async def save_to_s3(self, message: types.Message):
        image_name = "{0}.jpg".format(str(uuid.uuid4()))
        os.makedirs(self.image_dir, exist_ok=True)
        image_path = os.path.join(self.image_dir, image_name)
        await message.photo[-1].download(image_path)
        ## TODO work without S3 S3UploadFailedError
        s3_path = self.s3_client.save_image(image_path)
        os.remove(image_path)
        return s3_path

    @staticmethod
    def point_to_quadkey(lon: float, lat: float, zoom: int = 16) -> str:
        tile = mercantile.tile(lon, lat, zoom)
        return mercantile.quadkey(tile)

    @staticmethod
    def get_kafka_message(_cat_data: dict):
        if _cat_data["kafka_topic"] == "new_search":
            kafka_message = {"user_id": _cat_data["user_id"]}
        else:
            kafka_message = {
                "user_id": _cat_data["user_id"],
                "cat_name": _cat_data["cat_name"],
                "image_paths": _cat_data["s3_paths"],
                "additional_info": _cat_data["additional_info"],
                "quadkey": _cat_data["quadkey"],
                "person_name": _cat_data["person_name"],
            }
        return kafka_message

    async def send_msg_to_model(self, cat_data: dict):
        _cat_data = cat_data.copy()
        kafka_message = self.get_kafka_message(_cat_data)
        self.__kafka_producer.send(
            value=kafka_message,
            key=_cat_data["cat_name"],
            topic=_cat_data["kafka_topic"],
        )

        return True
