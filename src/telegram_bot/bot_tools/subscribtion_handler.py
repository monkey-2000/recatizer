from contextlib import suppress
from datetime import datetime

import cv2
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified
from aiogram.dispatcher.filters import Text

from src.services.user_profile_service import UserProfileClient
from src.telegram_bot.configs.bot_cfgs import bot_config
from src.utils.s3_client import YandexS3Client

s3_client = YandexS3Client(
    bot_config.s3_client_config.aws_access_key_id,
    bot_config.s3_client_config.aws_secret_access_key,
)

user_profile = UserProfileClient(bot_config.mongoDB_url)

UnsubscribeCb = CallbackData("fabnum", "action", "cat_id")


def get_keyboard_fab(cat_id, action="unsubsscribe"):

    if action == "unsubsscribe":
        text = "Unsubscribe"
    else:
        text = "Subscribe"

    buttons = [
        types.InlineKeyboardButton(
            text=text, callback_data=UnsubscribeCb.new(action=action, cat_id=cat_id)
        ),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


async def update_num_text_fab(message: types.Message, action: str, cat_id: str):
    with suppress(MessageNotModified):
        await message.edit_reply_markup(
            reply_markup=get_keyboard_fab(action=action, cat_id=cat_id)
        )


async def my_subscriptions(message: types.Message, state):
    cats = user_profile.find_all_user_cats(message.from_user.id)
    cats_data = await state.get_data()
    cats_data["cats"] = cats
    await state.update_data(cats_data)

    # TODO make fun
    if len(cats["find_cats"]) > 0:
        if len(cats["find_cats"]) == 1:
            msg = "<b>You found {0} cat. There is:</b>".format(len(cats["find_cats"]))
        else:
            msg = "<b>You found  {0} cats. There are:</b>".format(
                len(cats["find_cats"])
            )

        await message.answer(msg, parse_mode="HTML")

        await send_msgs_with_cats(message, cats["find_cats"])
    else:
        await message.answer(
            "You haven't uploaded the cats you found yet",
            reply_markup=types.ReplyKeyboardRemove(),
        )

    if len(cats["saw_cats"]) > 0:
        if len(cats["saw_cats"]) == 1:
            msg = "<b>You saw {0} cat. There is:</b>".format(len(cats["saw_cats"]))
        else:
            msg = "<b>You saw  {0} cats. There are:</b>".format(len(cats["saw_cats"]))

        await message.answer(msg, parse_mode="HTML")

        await send_msgs_with_cats(message, cats["saw_cats"])

    else:
        await message.answer(
            "You haven't lost your cat yet!", reply_markup=types.ReplyKeyboardRemove()
        )

    buttons = []
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    # buttons.append(types.KeyboardButton(text="Menu", callback_data=ReturnCb.new(
    #                                                                 action="return") ))
    buttons.append(types.KeyboardButton(text="Unsubscribe all"))
    keyboard.add(*buttons)
    await message.answer("That is all", reply_markup=keyboard)


async def subscribe_callback(call: types.CallbackQuery, callback_data: dict):
    cat_id = callback_data["cat_id"]
    user_profile.set_subscription_status(cat_id, set_status=False)

    await update_num_text_fab(call.message, action="subsscribe", cat_id=cat_id)
    await call.answer(text="You unsubsscribed")


async def unsubscribe_callback(call: types.CallbackQuery, callback_data: dict):
    cat_id = callback_data["cat_id"]
    user_profile.set_subscription_status(cat_id, set_status=True)

    await update_num_text_fab(call.message, action="unsubsscribe", cat_id=cat_id)
    await call.answer(text="You subsscribed")


async def unsubscribe_all(message: types.Message, state: FSMContext):
    cats_data = await state.get_data()
    cats = []
    cats.extend(cats_data["cats"]["saw_cats"])
    cats.extend(cats_data["cats"]["find_cats"])

    for cat in cats:
        user_profile.set_subscription_status(cat._id, set_status=False)
    await message.answer(text="You unsubsscribed from all cats")


async def send_msgs_with_cats(message, cats):
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

        cat_image = s3_client.load_image(cat.paths[0])
        n, m, _ = cat_image.shape

        cat_image = cv2.resize(cat_image, (100, 100))
        cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
        cat_image_bytes = cv2.imencode(".jpg", cat_image)[1].tobytes()

        await message.reply_photo(
            photo=cat_image_bytes,
            caption=comment,
            reply_markup=get_keyboard_fab(cat._id),
            parse_mode="HTML",
        )


def register_subscribtion_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        unsubscribe_callback, UnsubscribeCb.filter(action=["unsubsscribe"]), state="*"
    )
    dp.register_callback_query_handler(
        subscribe_callback, UnsubscribeCb.filter(action=["subsscribe"]), state="*"
    )
    dp.register_message_handler(
        my_subscriptions, Text(equals="My subscriptions", ignore_case=True), state="*"
    )
    dp.register_message_handler(
        unsubscribe_all, Text(equals="Unsubscribe all", ignore_case=True), state="*"
    )

