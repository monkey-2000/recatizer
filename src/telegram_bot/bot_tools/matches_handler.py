from datetime import datetime

import cv2
from aiogram import types, Dispatcher
from aiogram.types import InputMediaPhoto
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text

from src.services.user_profile_service import UserProfileClient
from src.telegram_bot.bot_tools.keyboards import get_callback_kb
from src.telegram_bot.configs.bot_cfgs import bot_config
from src.utils.s3_client import YandexS3Client

MatchesCb = CallbackData("matches", "action", "cat_id")
user_profile = UserProfileClient(bot_config.mongoDB_url)
s3_client = YandexS3Client(
    bot_config.s3_client_config.aws_access_key_id,
    bot_config.s3_client_config.aws_secret_access_key,
)

async def my_matches(message: types.Message, state):
    await message.answer("In dev")
    cats = user_profile.find_all_user_cats(message.from_user.id)
    cats = cats["find_cats"]
    await send_user_cats(message, cats)


async def send_user_cats(message, cats):
    for i, cat in enumerate(cats):
        sent_date = datetime.fromtimestamp(cat.dt)
        # TODO make good  format witiout msec
        comment = (
            "<b> Cat id {2}</b>\n"
            "Sending time{0}\n"
            "You wrote an info about: {1}".format(
                sent_date, cat.additional_info, cat._id
            )
        )
        keyboard = get_callback_kb(cat_id=cat._id,
                                   callback=MatchesCb ,
                                   action="show_matches",
                                   text="Show matches")
        await message.answer(
            text=comment, reply_markup=keyboard, parse_mode="HTML"
        )

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




async def show_matches(call: types.CallbackQuery, callback_data: dict):
    wanted_cat_id = callback_data["cat_id"]

    answers = user_profile.get_answers(wanted_cat_id)
    if len(answers) == 0:
        await call.message.answer(text="Sorry, this cat dont have any matches yet")


    for i, answer in enumerate(answers):
        cat = user_profile.cats_db.find({"_id": answer.match_cat_id})
        await show_match(call.message, cat[0])

    no_cat_kb = get_callback_kb(cat_id=wanted_cat_id,
                               callback=MatchesCb,
                               action="no_wanted_cat",
                               text="My cat is not here")


    await call.message.answer(text="Choose your cats please or:",
                              reply_markup=no_cat_kb)


async def mark_answer(call: types.CallbackQuery, callback_data: dict):
    # if
    wanted_cat_id = callback_data["cat_id"]
    if callback_data["action"] == "no_wanted_cat":
        await call.message.answer(
            text=f"IN DEV Sorry, We dont find your cat (we will remember your answer about {wanted_cat_id} IN DEV",\
            reply_markup=types.ReplyKeyboardRemove()
        )
    elif callback_data["action"] == "found_cat":
        await call.message.answer(
            text=f"IN DEV Yeeeeeeaaah, We hind your cat! we will remember your answer about {wanted_cat_id} IN DEV", \
            reply_markup=types.ReplyKeyboardRemove()
        )

    # elif "found_cat"

async def show_match(message, cat):
        # TODO make good  format witiout msec

        media_group = []
        for path in cat.paths:
            cat_image = s3_client.load_image(path)
            cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
            cat_image_bytes = cv2.imencode(".jpg", cat_image)[1].tobytes()
            media_group.append(InputMediaPhoto(media=cat_image_bytes))

        keyboard = get_callback_kb(cat_id=cat._id,
                                   callback= MatchesCb,
                                   action="found_cat",
                                   text="This my cat")


        sent_date = datetime.fromtimestamp(cat.dt)
        comment = (
            "Info about{0}".format(sent_date)
        )

        await message.reply_photo(
            photo=cat_image_bytes,
            caption=comment,
            reply_markup=keyboard,
            parse_mode="HTML",
        )


def register_add_links_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        show_matches, MatchesCb.filter(action=["show_matches"]), state="*"
    )
    dp.register_callback_query_handler(
        mark_answer, MatchesCb.filter(action=["no_wanted_cat", "found_cat"]), state="*"
    )
    dp.register_message_handler(
        my_matches, Text(equals="My matches", ignore_case=True), state="*"
    )
