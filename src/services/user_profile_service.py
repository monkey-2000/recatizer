import os
import uuid

import cv2
import mercantile
from aiogram import types
from aiogram.types import InputMediaPhoto, InputFile
from aiogram.utils.callback_data import CallbackData
from bson import ObjectId
from pymongo import MongoClient


from src.services.mongo_service import CatsMongoClient, PeopleMongoClient, AnswersMongoClient
from src.telegram_bot.bot_tools.keyboards import get_match_kb
from src.telegram_bot.configs.bot_base_configs import  TgBotConfig
from src.utils.s3_client import YandexS3Client


class UserProfileClient():
    MatchesCb = CallbackData("matches", "action", "match_id")
    def __init__(self,  config: TgBotConfig):
        client = MongoClient(config.mongoDB_url)
        self.cats_db = CatsMongoClient(client.main)
        self.people_db = PeopleMongoClient(client.main)
        self.answers_db = AnswersMongoClient(client.main)
        self.image_dir = config.image_dir
        self.s3_client = YandexS3Client(
            config.s3_client_config.aws_access_key_id,
            config.s3_client_config.aws_secret_access_key,
        )
    async def send_match(self, message, cat, match_id):
        keyboard = self.get_match_kb(match_id)

        os.makedirs(self.image_dir, exist_ok=True)
        media_group = types.MediaGroup()
        for path in cat.paths:
            cat_image = self.s3_client.load_image(path)
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
        await  message.answer(text=cat.additional_info, reply_markup=keyboard)





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
#     def find_all_user_cats(self, chat_id: int):
#         query = {"chat_id": chat_id, "is_active": True}
#         user_cats = {}
#         user_cats["saw_cats"] = self.cats_db.find(query)
#         user_cats["find_cats"] = self.people_db.find(query)
#         return user_cats
# # TODO need to connection via tables. The unsub, dont show matches with cat
#     def get_wanted_cats(self, chat_id: int):
#         query = {"chat_id": chat_id, "is_active": True}
#         user_cats = self.people_db.find(query)
#         return user_cats
#
#     def get_saw_cats(self, chat_id: int):
#         query = {"chat_id": chat_id, "is_active": True}
#         user_cats = self.cats_db.find(query)
#         return user_cats
#
#     def get_answers(self, wanted_cat_id: str):
#         wanted_cat_id = ObjectId(wanted_cat_id)
#         query = {"wanted_cat_id": wanted_cat_id}
#         user_cats = self.answers_db.find(query)
#         return user_cats
#
#
#     def cats_dbfind(self, query):
#         return self.cats_db.find(query)
#
#     # def get_matche(self, match_cat_id: ObjectId):
#     #
#     #     query =  {"_id": match_cat_id}
#     #     match_cats = self.cats.find(query)
#     #     return match_cats
#
#     def set_subscription_status(self, cat_id: str, set_status: bool):
#         cat_mongo_id = ObjectId(cat_id)
#
#         # cat_saw = self.cats_db.find( {"_id": cat_mongo_id})
#         # if cat_saw:
#         #     cat_saw = cat_saw[0]
#         #     cat_saw.is_active = set_status
#         #     self.cats_db.update(cat_saw)
#         #     return True
#         cat_find = self.people_db.find({"_id": cat_mongo_id})
#         if cat_find:
#             cat_find = cat_find[0]
#             cat_find.is_active = set_status
#             self.people_db.update(cat_find)
#             return True







