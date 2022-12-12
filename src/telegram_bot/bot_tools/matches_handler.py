
from datetime import datetime

import cv2
from aiogram import types, Dispatcher
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text

from src.services.user_profile_service import UserProfileClient
from src.telegram_bot.configs.bot_cfgs import bot_config

MatchesCb = CallbackData("matches", "action", "cat_id")
user_profile = UserProfileClient(bot_config.mongoDB_url)


async def my_matches(message: types.Message, state):
    await message.answer(
        "In dev")
    cats = user_profile.find_all_user_cats(message.from_user.id)
    cats = cats["find_cats"]
    await send_user_cats(message, cats)


async def send_user_cats(message, cats):
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


def get_keyboard_matches(cat_id, action="show_matches", text='Show matches'):


    buttons = [
        types.InlineKeyboardButton(text=text, callback_data=MatchesCb.new(
                                                                    action=action,
                                                                    cat_id=cat_id)),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


async def show_matches(call: types.CallbackQuery, callback_data: dict):
    cat_id = callback_data["cat_id"]
    print(cat_id)
    await call.message.answer(text=cat_id )


def register_add_links_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(show_matches, MatchesCb.filter(action=["show_matches"]), state="*")
    dp.register_message_handler(my_matches, Text(equals="My matches", ignore_case=True), state="*")
