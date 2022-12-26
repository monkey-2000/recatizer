
from pymongo import MongoClient

from src.cats_queue.producer import Producer
from src.services.mongo_service import CatsMongoClient, PeopleMongoClient, AnswersMongoClient
from src.telegram_bot.configs.bot_base_configs import  TgBotConfig
from src.utils.s3_client import YandexS3Client

import os
import uuid

import cv2
import mercantile
from aiogram import types
from aiogram.types import InputMediaPhoto, InputFile
from aiogram.utils.callback_data import CallbackData


class MatchSender():

    MatchesCb = CallbackData("matches", "action", "match_id")

    def __init__(self, image_dir):
        self.image_dir = image_dir

    async def send_match(self, message, cat, cat_images, match_id):
        keyboard = self.get_match_kb(match_id)

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
        await message.answer_media_group( media=media_group)
        await message.answer(text=cat.additional_info, reply_markup=keyboard)


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
class UserProfileClient():

    def __init__(self,  config: TgBotConfig):
        client = MongoClient(config.mongoDB_url)
        self.cats_db = CatsMongoClient(client.main)
        self.people_db = PeopleMongoClient(client.main)
        self.answers_db = AnswersMongoClient(client.main)
       # self.image_dir = config.image_dir
        self.s3_client = YandexS3Client(
            config.s3_client_config.aws_access_key_id,
            config.s3_client_config.aws_secret_access_key,
        )
        self.image_dir = config.image_dir
        self.__sender = MatchSender(self.image_dir)
        self.__kafka_producer = Producer()

    async def send_match(self, message: types.Message, cat, match_id):

        cat_images = []
        for path in cat.paths:
            cat_image = self.s3_client.load_image(path)
            cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
            # cat_image = cv2.imencode(".jpg", cat_image)[1].tobytes()
            cat_images.append(cat_image)
        await self.__sender.send_match(message, cat, cat_images, match_id)

    async def save_to_s3(self, message: types.Message):
        image_name = "{0}.jpg".format(str(uuid.uuid4()))
        os.makedirs(self.image_dir, exist_ok=True)
        image_path = os.path.join(self.image_dir, image_name)
        await message.photo[-1].download(image_path)
        s3_path = self.s3_client.save_image(image_path)
        os.remove(image_path)
        return s3_path

    @staticmethod
    def point_to_quadkey(lon: float, lat: float, zoom: int = 16) -> str:
        tile = mercantile.tile(lon, lat, zoom)
        return mercantile.quadkey(tile)

    # @staticmethod
    # async def update_data(state, paths: list, cat_name, person_name, user_id):
    #
    #     if person_name == None:
    #         person_name = "BORIS BRITVA"  ## TODO add name generator service
    #     await state.update_data(
    #         s3_paths=paths, cat_name=cat_name, person_name=person_name, user_id=user_id
    #     )

    @staticmethod
    def get_kafka_message(_cat_data: dict):
        kafka_message = {
            "user_id": _cat_data["user_id"],
            "cat_name": _cat_data["cat_name"],
            "image_paths": _cat_data["s3_paths"],
            "additional_info": _cat_data["additional_info"],
            "quadkey": _cat_data["quadkey"],
            "person_name": _cat_data["person_name"],
        }
        return kafka_message

    async def send_msgs_to_model(self, cat_data: dict):
        _cat_data = cat_data.copy()
        kafka_message = self.get_kafka_message(_cat_data)
        self.__kafka_producer.send(
            value=kafka_message,
            key=_cat_data["cat_name"],
            topic=_cat_data["kafka_topic"],
        )

        return True




