import uuid


from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from src.telegram_bot.bot_tools.keyboards import get_extra_info_kb, get_share_location_kb, get_main_menu_kb, \
    get_contact_name_kb
from src.telegram_bot.bot_tools.states import RStates
from src.telegram_bot.configs.bot_cfgs import bot_config
from src.telegram_bot.bot_tools.user_profile_service import UserProfileClient

user_profile = UserProfileClient(bot_config)


async def save_album_to_s3(
    message: types.Message, album: list, state: FSMContext, cat_name: str
):
    """This handler will receive a complete album of any type."""

    s3_paths = []
    if len(album) > bot_config.max_load_photos:
        album = album[:bot_config.max_load_photos]
        await message.answer(
                    text=f"You uploaded a lot of photos. We have selected the top {bot_config.max_load_photos}")
    for message in album:
        if message.photo:
            s3_path = await user_profile.save_to_s3(message)
            s3_paths.append(s3_path)
    await state.update_data(
        s3_paths=s3_paths, cat_name=cat_name, user_id=message.from_user.id
    )
    await ask_about_name_and_tg(message, state)


async def save_photo_to_s3(message: types.Message, state: FSMContext, cat_name: str):
    s3_path = await user_profile.save_to_s3(message)
    await state.update_data(
        s3_paths=[s3_path], cat_name=cat_name, user_id=message.from_user.id
    )
    await ask_about_name_and_tg(message, state)

async def ask_about_name_and_tg(message, state):
    await state.set_state(RStates.ask_name_contact)
    await message.answer("Do you want to leave your @tg and name? (yes/no)", reply_markup=get_contact_name_kb())


async def get_name_and_tg(message: types.Message, state: FSMContext):
     person_name = None
     if message.text.lower() == "yes":

        person_name = "{0} (tg: @{1})".format(
            message.from_user.first_name, message.from_user.username
        )
     elif message.text.lower() == "no":
        person_name = "NONAME"  ## TODO add name generator service
     if person_name:
         await state.update_data(person_name=person_name)
         await ask_about_additional_info(message,state)
     else:
        await ask_about_name_and_tg(message, state)

async def ask_about_additional_info(message, state):
    await state.set_state(RStates.ask_extra_info)
    await message.answer("Please write us additional info in TEXT MESSAGE about this cat or press no",
                         reply_markup=get_extra_info_kb())


# async def get_extra_info(message: types.Message, state: FSMContext):
#      await message.answer("Please write us additional info in TEXT MESSAGE about this cat.")
#      await state.set_state(RStates.wait_extra_info)


async def ask_about_location(message: types.Message, state: FSMContext):
    if message.text.lower() == "no":
        await state.update_data(additional_info="no info")
    else:
        await state.update_data(additional_info=message.text)

    await message.answer("Would you like to share your location?",
                         reply_markup=get_share_location_kb())
    await state.set_state(RStates.geo)


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
    is_sent = await user_profile.send_msgs_to_model(cat_data)

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
        save_album_to_s3, is_media_group=True,  content_types=types.ContentType.ANY, state=[RStates.find, RStates.saw])

    dp.register_message_handler(
        save_photo_to_s3, content_types=["photo"], state=[RStates.find, RStates.saw])

    # dp.register_message_handler(
    #     get_extra_info, Text(equals=["Yes"], ignore_case=True), state=RStates.ask_extra_info)

    dp.register_message_handler(
        ask_about_location, state=[RStates.ask_extra_info],
        content_types=["text"])

    dp.register_message_handler(
        get_name_and_tg, content_types=["text"], state=RStates.ask_name_contact)

    dp.register_message_handler(
        handle_location,
        state=RStates.geo,
        content_types=["location"])

    dp.register_message_handler(
        without_handle_location, Text(equals="No", ignore_case=True), state=RStates.geo)

