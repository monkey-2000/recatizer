import asyncio
import os
import uuid

import mercantile
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import BotCommand, Dice, ContentType



from src.telegram_bot.bot_tools.find_cat_handlers import register_find_cat_handlers
from src.telegram_bot.bot_tools.keyboards import get_main_menu_kb
from src.telegram_bot.bot_tools.main_menu_text import start_menu_text, saw_lost_menu_text
from src.telegram_bot.bot_tools.match_callbacks import register_match_handlers
from src.telegram_bot.bot_tools.save_new_cat_handlers import register_save_new_cat_handlers
from src.telegram_bot.bot_tools.saw_cat_handlers import register_saw_cat_handlers

from src.telegram_bot.bot_tools.states import RStates
from src.telegram_bot.bot_tools.user_profile_service import UserProfileClient

from src.telegram_bot.configs.bot_cfgs import bot_config
from src.cats_queue.producer import Producer
from src.telegram_bot.middleware import AlbumMiddleware




storage = MemoryStorage()
# kafka_producer = Producer()

bot = Bot(token=bot_config.token)

# user_profile = UserProfileClient(bot_config)

dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(AlbumMiddleware())

register_find_cat_handlers(dp)
register_saw_cat_handlers(dp)
register_match_handlers(dp)
register_save_new_cat_handlers(dp)





async def set_commands(bot: Bot):
    commands = [BotCommand(command='/start', description="go to main menu")]
                # BotCommand(command='/matches', description="show matches"),
                # BotCommand(command='/my_cat', description="show my cats")]
    await bot.set_my_commands(commands)



@dp.message_handler(commands=["start"], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    keyboard = get_main_menu_kb()
    await message.answer(
        text=start_menu_text,
        reply_markup=keyboard,
    )


# @dp.message_handler(Text(equals="saw cat", ignore_case=True))
# async def saw_cat(message: types.Message, state: FSMContext):
#     await message.answer(saw_lost_menu_text
#         , reply_markup=types.ReplyKeyboardRemove()
#     )
#     await state.set_state(RStates.saw)
#     await state.update_data(kafka_topic="saw_cat")


# async def save_to_s3(message):
#     image_name = "{0}.jpg".format(str(uuid.uuid4()))
#     os.makedirs(bot_config.image_dir, exist_ok=True)
#     image_path = os.path.join(bot_config.image_dir, image_name)
#     await message.photo[-1].download(image_path)
#     s3_path = user_profile.s3_client.save_image(image_path)
#     os.remove(image_path)
#     return s3_path
#
#
# def point_to_quadkey(lon: float, lat: float, zoom: int = 16) -> str:
#     tile = mercantile.tile(lon, lat, zoom)
#     return mercantile.quadkey(tile)
#
#
# async def update_data(state, paths: list, cat_name, person_name, user_id):
#
#     if person_name == None:
#         person_name = "BORIS BRITVA"  ## TODO add name generator service
#     await state.update_data(
#         s3_paths=paths, cat_name=cat_name, person_name=person_name, user_id=user_id
#     )
#
#
# @dp.message_handler(
#     is_media_group=True,
#     content_types=types.ContentType.ANY,
#     state=[RStates.find, RStates.saw],
# )
# async def save_album_to_s3(
#     message: types.Message, album: list, state: FSMContext, cat_name: str
# ):
#     """This handler will receive a complete album of any type."""
#
#     s3_paths = []
#     if len(album) > bot_config.max_load_photos:
#         album = album[:bot_config.max_load_photos]
#         await message.answer(
#                     text=f"You uploaded a lot of photos. We have selected the top {bot_config.max_load_photos}")
#     for message in album:
#         if message.photo:
#             s3_path = await save_to_s3(message)
#             s3_paths.append(s3_path)
#
#     await state.set_state(RStates.ask_extra_info)
#
#     person_name = "{0} ({1})".format(
#         message.from_user.first_name, message.from_user.username
#     )
#
#     await update_data(state, s3_paths, cat_name, person_name, message.from_user.id)
#
#     await message.answer("Please write some extra info about this cat")
#
#
# @dp.message_handler(content_types=["photo"], state=[RStates.find, RStates.saw])
# async def save_photo_to_s3(message: types.Message, state: FSMContext, cat_name: str):
#     s3_path = await save_to_s3(message)
#     await state.set_state(RStates.ask_extra_info)
#     person_name = "{0} ({1})".format(
#         message.from_user.first_name, message.from_user.username
#     )
#     await update_data(state, [s3_path], cat_name, person_name, message.from_user.id)
#     await message.answer("Please write some extra info about this cat")
#
#
# @dp.message_handler(state=RStates.ask_extra_info, content_types=["text"])
# async def get_extra_info_and_send(message: types.Message, state: FSMContext):
#     await state.update_data(additional_info=message.text)
#     reply = "Would you like to share your location?"
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     buttons = []
#     buttons.append(types.KeyboardButton(text="Yes", request_location=True))
#     buttons.append(types.KeyboardButton(text="No"))
#     keyboard.add(*buttons)
#     await message.answer(reply, reply_markup=keyboard)
#     await state.set_state(RStates.geo)
#
#
# @dp.message_handler(state=RStates.geo, content_types=["location"])
# async def handle_location(message: types.Message, state: FSMContext):
#     lat = message.location.latitude
#     lon = message.location.longitude
#     quadkey = point_to_quadkey(lon, lat)
#     cat_data = await state.get_data()
#     cat_data["quadkey"] = quadkey
#     cat_data["cat_id"] = str(uuid.uuid4())
#     is_sent = await send_msgs_to_model(cat_data)
#     if not is_sent:
#         await message.answer(
#             reply="Sorry. Try again", reply_markup=types.ReplyKeyboardRemove()
#         )
#     await message.answer(
#         "Thanks! We notify you when we'll get any news",
#         reply_markup=types.ReplyKeyboardRemove(),
#     )
#     await state.finish()
#
#
# @dp.message_handler(Text(equals="No", ignore_case=True), state=RStates.geo)
# async def handle_location(message: types.Message, state: FSMContext):
#     cat_data = await state.get_data()
#     # cat_data["quadkey"] = None # TODO fix it
#     cat_data["quadkey"] = "no_quad"
#     is_sent = await send_msgs_to_model(cat_data)
#
#     if not is_sent:
#         await message.answer(
#             reply="Sorry. Try again", reply_markup=types.ReplyKeyboardRemove()
#         )
#     await message.answer(
#         "Thanks! We notify you when we'll get any news",
#         reply_markup=types.ReplyKeyboardRemove(),
#     )
#     await state.finish()




#@dp.message_handler(commands=["not_may_cat"], state="*")
@dp.message_handler(commands=['help'], state="*")
async def show_matches(message: types.Message, state: FSMContext):
    await message.answer(f'You value is ')


# def get_kafka_message(_cat_data):
#     kafka_message = {
#         "user_id": _cat_data["user_id"],
#         "cat_name": _cat_data["cat_name"],
#         "image_paths": _cat_data["s3_paths"],
#         "additional_info": _cat_data["additional_info"],
#         "quadkey": _cat_data["quadkey"],
#         "person_name": _cat_data["person_name"],
#     }
#     return kafka_message
#
#
# async def send_msgs_to_model(cat_data):
#     _cat_data = cat_data.copy()
#     kafka_message = get_kafka_message(_cat_data)
#     kafka_producer.send(
#         value=kafka_message,
#         key=_cat_data["cat_name"],
#         topic=_cat_data["kafka_topic"],
#     )
#
#     return True


async def main():
    await set_commands(bot)
    await dp.skip_updates()
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())



