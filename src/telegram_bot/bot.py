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
from src.utils.s3_client import YandexS3Client


bot = Bot(token=bot_config.token)
storage = MemoryStorage()
kafka_producer = Producer()
dp = Dispatcher(bot, storage=storage)
s3_client = YandexS3Client(bot_config.s3_client_config.aws_access_key_id, bot_config.s3_client_config.aws_secret_access_key)
class QStates(StatesGroup):
    saw = State()
    find = State()
    geo = State()

def point_to_quadkey(lon: float, lat: float, zoom: int = 16) -> str:
    tile = mercantile.tile(lon, lat, zoom)
    return mercantile.quadkey(tile)

def to_message(user_id: str, image_path: str, additional_info: str, quadkey: str = 'no quad'):
    return {'user_id': user_id,
                 'image_path': image_path,
                 'additional_info': additional_info,
                 'quadkey': quadkey}

async def save_to_s3(message):
    image_name = "{0}.jpg".format(str(uuid.uuid4()))
    os.makedirs(bot_config.image_dir, exist_ok=True)
    image_path = os.path.join(bot_config.image_dir, image_name)
    await message.photo[-1].download(image_path)
    s3_path = s3_client.save_image(image_path)
    os.remove(image_path)
    return s3_path

@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = []
    buttons.append(types.KeyboardButton(text="I saw a cat"))
    buttons.append(types.KeyboardButton(text="I lost my cat"))
    keyboard.add(*buttons)
    await message.answer("Please press the button 'I lost my cat' if you are looking for your cat, and the another one if you saw someone's cat", reply_markup=keyboard)


@dp.message_handler(Text(equals="I lost my cat", ignore_case=True))
async def lost_cat(message: types.Message, state: FSMContext):
    await message.answer("Please upload photo of your cat",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(QStates.find)


@dp.message_handler(Text(equals="I saw a cat", ignore_case=True))
async def saw_cat(message: types.Message, state: FSMContext):
    await message.answer("Please upload photo of cat",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(QStates.saw)

@dp.message_handler(state=QStates.find, content_types=['photo'])
async def process_find(message: types.Message, state: FSMContext):
    additional_info = message.to_python().get("caption", "")
    s3_path = await save_to_s3(message)
    reply = "Would you like to share your location?"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton('Yes', request_location=True))
    buttons.append(types.KeyboardButton(text="No"))
    keyboard.add(*buttons)
    await message.answer(reply, reply_markup=keyboard)
    await state.set_state(QStates.geo)
    await state.update_data(s3_path=s3_path,
                            additional_info=additional_info,
                            kafka_topic='find_cat')

@dp.message_handler(state=QStates.saw, content_types=['photo'])
async def process_saw(message: types.Message, state: FSMContext):
    additional_info = message.to_python().get("caption", "")
    s3_path = await save_to_s3(message)
    reply = "Would you like to share your location?"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton('Yes', request_location=True))
    buttons.append(types.KeyboardButton(text="No"))
    keyboard.add(*buttons)
    await message.answer(reply, reply_markup=keyboard)
    await state.set_state(QStates.geo)
    await state.update_data(s3_path=s3_path,
                            additional_info=additional_info,
                            kafka_topic='saw_cat')

@dp.message_handler(state=QStates.geo, content_types=['location'])
async def handle_location(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    quadkey = point_to_quadkey(lon, lat)
    user_data = await state.get_data()
    kafka_message = to_message(message.from_user.id, user_data['s3_path'], user_data['additional_info'], quadkey)
    kafka_producer.send(value=kafka_message, key=id, topic=user_data['kafka_topic'])
    reply = "Thanks!"
    await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())
    # await state.update_data(quadkey=quadkey)

    # перенести в другой хэндлер
    # user_data = await state.get_data()
    # kafka_message = to_message(message.from_user.id, user_data['s3_path'],
    #                            user_data['additional_info'], user_data['quadkey'])
    # kafka_producer.send(value=kafka_message, key=id, topic=user_data['kafka_topic'])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, timeout=10*60)
