import uuid


from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


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

    await state.set_state(RStates.ask_extra_info)

    person_name = "{0} ({1})".format(
        message.from_user.first_name, message.from_user.username
    )

    if person_name == None:
        person_name = "BORIS BRITVA"  ## TODO add name generator service
    await state.update_data(
        s3_paths=s3_paths, cat_name=cat_name, person_name=person_name, user_id=message.from_user.id
    )

    await message.answer("Please write some extra info about this cat")



async def save_photo_to_s3(message: types.Message, state: FSMContext, cat_name: str):
    s3_path = await user_profile.save_to_s3(message)
    await state.set_state(RStates.ask_extra_info)
    person_name = "{0} ({1})".format(
        message.from_user.first_name, message.from_user.username
    )
    await user_profile.update_data(state, [s3_path], cat_name, person_name, message.from_user.id)
    await message.answer("Please write some extra info about this cat")



async def get_extra_info_and_send(message: types.Message, state: FSMContext):
    await state.update_data(additional_info=message.text)
    reply = "Would you like to share your location?"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(text="Yes", request_location=True))
    buttons.append(types.KeyboardButton(text="No"))
    keyboard.add(*buttons)
    await message.answer(reply, reply_markup=keyboard)
    await state.set_state(RStates.geo)



async def handle_location(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    quadkey = user_profile.point_to_quadkey(lon, lat)
    cat_data = await state.get_data()
    cat_data["quadkey"] = quadkey
    cat_data["cat_id"] = str(uuid.uuid4())
    is_sent = await user_profile.send_msgs_to_model(cat_data)
    if not is_sent:
        await message.answer(
            reply="Sorry. Try again", reply_markup=types.ReplyKeyboardRemove()
        )
    await message.answer(
        "Thanks! We notify you when we'll get any news",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.finish()



async def without_handle_location(message: types.Message, state: FSMContext):
    cat_data = await state.get_data()
    # cat_data["quadkey"] = None # TODO fix it
    cat_data["quadkey"] = "no_quad"
    is_sent = await user_profile.send_msgs_to_model(cat_data)

    if not is_sent:
        await message.answer(
            reply="Sorry. Try again", reply_markup=types.ReplyKeyboardRemove()
        )
    await message.answer(
        "Thanks! We notify you when we'll get any news",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.finish()




def register_save_new_cat_handlers(dp: Dispatcher):
    dp.register_message_handler(
        save_album_to_s3, is_media_group=True,  content_types=types.ContentType.ANY, state=[RStates.find, RStates.saw])

    dp.register_message_handler(
        save_photo_to_s3, content_types=["photo"], state=[RStates.find, RStates.saw])

    dp.register_message_handler(
        get_extra_info_and_send, state=RStates.ask_extra_info, content_types=["text"])

    dp.register_message_handler(
        handle_location, state=RStates.geo, content_types=["location"])

    dp.register_message_handler(
        without_handle_location, Text(equals="No", ignore_case=True), state=RStates.geo)

