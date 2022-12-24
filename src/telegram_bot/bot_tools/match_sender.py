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