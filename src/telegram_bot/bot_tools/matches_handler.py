
from datetime import datetime

import cv2
from aiogram import types
from aiogram.utils.callback_data import CallbackData



MatchesCb = CallbackData("matches", "action", "cat_id")

async def send_matches_cats(message, cats):
    for i, cat in enumerate(cats):
        sent_date = datetime.fromtimestamp(cat.dt)
        # TODO make good  format witiout msec
        comment = "<b> Cat id {2}</b>\n"\
                  "Sending time{0}\n" \
                  "You wrote an info about: {1}".format(sent_date, cat.additional_info, cat._id)

        await message.answer(

                                text=comment ,
                                reply_markup=get_keyboard_matches(cat._id),
                                parse_mode="HTML")

        # cat_image = s3_client.load_image(cat.paths[0])
        # n, m, _ = cat_image.shape
        #
        # cat_image = cv2.resize(cat_image, (100, 100))
        # cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
        # cat_image_bytes = cv2.imencode(".jpg", cat_image)[1].tobytes()
        #
        # await message.reply_photo(
        #                         photo=cat_image_bytes,
        #                         caption=comment ,
        #                         reply_markup=get_keyboard_matches(cat._id),
        #                         parse_mode="HTML")


def get_keyboard_matches(cat_id, action="show_matches"):


    buttons = [
        types.InlineKeyboardButton(text='Show matches', callback_data=MatchesCb.new(
                                                                    action=action,
                                                                    cat_id=cat_id)),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard