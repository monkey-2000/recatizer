import os
import uuid

import mercantile
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from src.telegram_bot.configs.bot_cfgs import bot_config
from src.cats_queue.producer import Producer
from src.telegram_bot.middleware import AlbumMiddleware
from src.utils.s3_client import YandexS3Client


bot = Bot(token=bot_config.token)
storage = MemoryStorage()
kafka_producer = Producer()
dp = Dispatcher(bot, storage=storage)
s3_client = YandexS3Client(
    bot_config.s3_client_config.aws_access_key_id,
    bot_config.s3_client_config.aws_secret_access_key,
)


class RStates(StatesGroup):
    saw = State()
    find = State()
    geo = State()
    ask_extra_info = State()
    send_message = State()


@dp.message_handler(commands=["start"], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = []
    buttons.append(types.KeyboardButton(text="I saw a cat"))
    buttons.append(types.KeyboardButton(text="I lost my cat"))
    keyboard.add(*buttons)
    await message.answer(
        "Please press the button 'I lost my cat' if you are looking for your cat, and the another one if you saw someone's cat",
        reply_markup=keyboard,
    )


@dp.message_handler(Text(equals="I lost my cat", ignore_case=True))
async def lost_cat(message: types.Message, state: FSMContext):
    await message.answer(
        "Please upload photo of your cat", reply_markup=types.ReplyKeyboardRemove()
    )

    await state.set_state(RStates.find)
    await state.update_data(kafka_topic="find_cat")


@dp.message_handler(Text(equals="I saw a cat", ignore_case=True))
async def saw_cat(message: types.Message, state: FSMContext):
    await message.answer(
        "Please upload photo of cat", reply_markup=types.ReplyKeyboardRemove()
    )

    await state.set_state(RStates.saw)
    await state.update_data(kafka_topic="saw_cat")


async def save_to_s3(message):
    image_name = "{0}.jpg".format(str(uuid.uuid4()))
    os.makedirs(bot_config.image_dir, exist_ok=True)
    image_path = os.path.join(bot_config.image_dir, image_name)
    await message.photo[-1].download(image_path)
    s3_path = s3_client.save_image(image_path)
    os.remove(image_path)
    return s3_path


def point_to_quadkey(lon: float, lat: float, zoom: int = 16) -> str:
    tile = mercantile.tile(lon, lat, zoom)
    return mercantile.quadkey(tile)


async def update_data(state, paths: list, cat_name, person_name, user_id):
    await state.update_data(
        s3_paths=paths,
        cat_name=cat_name,
        person_name=person_name,
        user_id=user_id
    )

@dp.message_handler(
    is_media_group=True,
    content_types=types.ContentType.ANY,
    state=[RStates.find, RStates.saw],
)
async def save_album_to_s3(
    message: types.Message, album: list, state: FSMContext, cat_name: str
):
    """This handler will receive a complete album of any type."""

    s3_paths = []
    for message in album:
        if message.photo:
            s3_path = await save_to_s3(message)
            s3_paths.append(s3_path)

    await state.set_state(RStates.ask_extra_info)
    await  update_data(state, s3_paths, cat_name, None, message.from_user.id)

    await message.answer("Please write some extra info about this cat")


@dp.message_handler(content_types=["photo"], state=[RStates.find, RStates.saw])
async def save_photo_to_s3(message: types.Message, state: FSMContext, cat_name: str):
    s3_path = await save_to_s3(message)
    await state.set_state(RStates.ask_extra_info)
    await  update_data(state, [s3_path], cat_name, None, message.from_user.id)
    await message.answer("Please write some extra info about this cat")


@dp.message_handler(state=RStates.ask_extra_info, content_types=["text"])
async def get_extra_info_and_send(message: types.Message, state: FSMContext):
    await state.update_data(additional_info=message.text)
    reply = "Would you like to share your location?"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton("Yes", request_location=True))
    buttons.append(types.KeyboardButton(text="No"))
    keyboard.add(*buttons)
    await message.answer(reply, reply_markup=keyboard)
    await state.set_state(RStates.geo)


@dp.message_handler(state=RStates.geo, content_types=["location"])
async def handle_location(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    quadkey = point_to_quadkey(lon, lat)
    cat_data = await state.get_data()
    cat_data["quadkey"] = quadkey

    is_sent = await send_msgs_to_model(cat_data)
    if not is_sent:
        await message.answer(
            reply="Sorry. Try again", reply_markup=types.ReplyKeyboardRemove()
        )
    await message.answer(
        "Thanks! We notify you when we'll get any news",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.finish()


@dp.message_handler(Text(equals="No", ignore_case=True), state=RStates.geo)
async def handle_location(message: types.Message, state: FSMContext):
    cat_data = await state.get_data()
    #cat_data["quadkey"] = None # TODO fix it
    cat_data["quadkey"] = 'no_quad'
    is_sent = await send_msgs_to_model(cat_data)
    if not is_sent:
        await message.answer(
            reply="Sorry. Try again", reply_markup=types.ReplyKeyboardRemove()
        )
    await message.answer(
        "Thanks! We notify you when we'll get any news",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.finish()


def get_kafka_message(_cat_data):
    kafka_message = {
        "user_id": _cat_data["user_id"],
        "image_paths": _cat_data["s3_paths"],
        "additional_info": _cat_data["additional_info"],
        "quadkey": _cat_data["quadkey"],
        "person_name": _cat_data["person_name"],
    }
    return kafka_message


async def send_msgs_to_model(cat_data):
    _cat_data = cat_data.copy()
    kafka_message = get_kafka_message(_cat_data)
    kafka_producer.send(
        value=kafka_message,
        key=_cat_data["cat_name"],
        topic=_cat_data["kafka_topic"],
    )

    return True


if __name__ == "__main__":
    dp.middleware.setup(AlbumMiddleware())
    executor.start_polling(dp, skip_updates=True, timeout=10 * 60)
