import uuid


from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from src.telegram_bot.bot_tools.keyboards import (
    get_extra_info_kb,
    get_share_location_kb,
    get_main_menu_kb
)
from src.telegram_bot.bot_tools.states import RStates
from src.telegram_bot.configs.bot_cfgs import bot_config
from src.telegram_bot.bot_tools.user_profile_service import UserProfileClient

user_profile = UserProfileClient(bot_config)
ContactCb = CallbackData("user_contact", "action", "field_key")
class SaveCatStates(StatesGroup):
    geo = State()
    ask_user_info = State()
    ask_extra_info = State()
    wait_extra_info = State()
    editing_user_info = State()

async def save_album_to_s3(
    message: types.Message, album: list, state: FSMContext, cat_name: str
):
    """This handler will receive a complete album of any type."""

    s3_paths = []
    if len(album) > bot_config.max_load_photos:
        album = album[: bot_config.max_load_photos]
        await message.answer(
            text=f"You uploaded a lot of photos. We have selected the top {bot_config.max_load_photos}"
        )
    for message in album:
        if message.photo:
            s3_path = await user_profile.save_to_s3(message)
            s3_paths.append(s3_path)
    await state.update_data(
        s3_paths=s3_paths, cat_name=cat_name, user_id=message.from_user.id
    )
    await ask_about_contacts(message, state)


async def save_photo_to_s3(message: types.Message, state: FSMContext, cat_name: str):
    s3_path = await user_profile.save_to_s3(message)
    await state.update_data(
        s3_paths=[s3_path], cat_name=cat_name, user_id=message.from_user.id
    )
    await ask_about_contacts(message, state)


async def ask_about_contacts(message, state):
    await state.set_state(SaveCatStates.ask_user_info)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(text="Yes"))
    buttons.append(types.KeyboardButton(text="No"))
    keyboard.add(*buttons)

    await message.answer(
        "Do you want to leave your contacts? (yes/no)",
        reply_markup=keyboard,
    )



async def edit_user_info(message: types.Message, state: FSMContext):

    if message.text.lower() in ["yes", "edit"]:
        user_info = {"name": message.from_user.first_name,
                     "contacts": f"tg: @{message.from_user.username}"}
        await state.update_data(user_info=user_info)
        state_data = await state.get_data()
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton(text="Send"))
        await message.answer(
            text=f"Edit your name and contacts and click 'Send'.",
            reply_markup=kb
        )
        field_kb = get_field_kb(state_data["user_info"])

        await state.set_state(SaveCatStates.editing_user_info)
        await message.answer(
            text="Сlick what you want to edit:",
            reply_markup=field_kb)
    elif message.text.lower() == "send":
       await send_contact_info(message, state)
    elif message.text.lower() == "no":
        person_name = "NONAME"  ## TODO add name generator service
        await state.update_data(person_name=person_name)
        await ask_about_additional_info(message, state)
    else:
        await ask_about_contacts(message, state)

async def send_contact_info(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    person_name = "{0} (contacts: {1})".format(state_data["user_info"]["name"],
                                               state_data["user_info"]["contacts"])
    await state.update_data(person_name=person_name)
    await ask_about_additional_info(message, state)

def get_field_kb(user_info: dict):
    field_kb = types.InlineKeyboardMarkup(row_width=1)
    for key in user_info:
        field_kb.add(types.InlineKeyboardButton("{0}: {1}".format(key, user_info[key]),
                                                callback_data=ContactCb.new(action="edit", field_key=key)))
    return field_kb


async def editing_user_info(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.update_data(editing_msg=call.message, editing_field=callback_data["field_key"])
    msg_text = r"_It is not the message you are looking for\.\.\._"
    # msg = await call.message.answer(
    #                              msg_text,
    #                              reply_markup=types.ReplyKeyboardRemove(),
    #                              parse_mode="MarkdownV2")
    # await msg.delete()

    await call.answer(text="Send new message with a new {0} value.".format(callback_data["field_key"]), show_alert=True)



async def update_user_info(message: types.Message, state: FSMContext):
    if message.text.lower() == "send":
        await send_contact_info(message, state)
        return
    state_data = await state.get_data()
    await state.set_state(SaveCatStates.ask_user_info)
    user_info = state_data["user_info"]
    user_info[state_data["editing_field"]] = message.text
    await state.update_data(user_info=user_info)
    await state_data["editing_msg"].edit_reply_markup(get_field_kb(user_info))
    await message.delete()




async def ask_about_additional_info(message, state):
    await state.set_state(SaveCatStates.ask_extra_info)
    await message.answer(
        "Please write us additional info in TEXT MESSAGE about this cat or press no",
        reply_markup=get_extra_info_kb(),
    )




async def ask_about_location(message: types.Message, state: FSMContext):
    if message.text.lower() == "no":
        await state.update_data(additional_info="no info")
    else:
        await state.update_data(additional_info=message.text)

    await message.answer(
        "Would you like to share your location?", reply_markup=get_share_location_kb()
    )
    await state.set_state(SaveCatStates.geo)


async def handle_location(message: types.Message, state: FSMContext):

    lat = message.location.latitude
    lon = message.location.longitude
    quadkey = user_profile.point_to_quadkey(lon, lat)

    cat_data = await state.get_data()
    cat_data["quadkey"] = quadkey
    cat_data["cat_id"] = str(uuid.uuid4())

    await send_msg(message, cat_data)
    await state.finish()


async def without_handle_location(message: types.Message, state: FSMContext):
    cat_data = await state.get_data()

    # cat_data["quadkey"] = None # TODO fix it
    cat_data["quadkey"] = "no_quad"
    cat_data["cat_id"] = str(uuid.uuid4())
    await send_msg(message, cat_data)
    await state.finish()


async def send_msg(message, cat_data):
    is_sent = await user_profile.send_msg_to_model(cat_data)

    if not is_sent:
        await message.answer(
            reply="Sorry. Try again", reply_markup=types.ReplyKeyboardRemove()
        )
    if cat_data["kafka_topic"] == "saw_cat":
        finish_msg = "Thanks!"
    elif cat_data["kafka_topic"] == "find_cat":
        finish_msg = "Thanks! We notify you when we'll get any news"
    await message.answer(
        finish_msg,
        reply_markup=get_main_menu_kb(),
    )


def register_save_new_cat_handlers(dp: Dispatcher):
    dp.register_message_handler(
        save_album_to_s3,
        is_media_group=True,
        content_types=types.ContentType.ANY,
        state=[RStates.find, RStates.saw],
    )

    dp.register_message_handler(
        save_photo_to_s3, content_types=["photo"], state=[RStates.find, RStates.saw]
    )

    dp.register_message_handler(edit_user_info,
                                content_types=["text"],
                                state=[SaveCatStates.ask_user_info])


    dp.register_callback_query_handler(
        editing_user_info, ContactCb.filter(action=["edit"]),
        state=SaveCatStates.editing_user_info
    )

    dp.register_message_handler(
        update_user_info, content_types=["text"], state=SaveCatStates.editing_user_info
    )


    dp.register_message_handler(
        ask_about_location, state=[SaveCatStates.ask_extra_info], content_types=["text"]
    )

    dp.register_message_handler(
        handle_location, state=SaveCatStates.geo, content_types=["location"]
    )

    dp.register_message_handler(
        without_handle_location, Text(equals="No", ignore_case=True), state=SaveCatStates.geo
    )



