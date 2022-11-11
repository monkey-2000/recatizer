import os
import uuid

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from telegram_bot.configs.bot_cfgs import bot_config
from telegram_bot.queu.producer import Producer


bot = Bot(token=os.environ.get('BOT_TOKEN'))
storage = MemoryStorage()
kafka_producer = Producer()
dp = Dispatcher(bot, storage=storage)
class QStates(StatesGroup):
    saw = State()
    find = State()
    geo = State()

@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = []
    #user_data = await state.get_data()
    #print(user_data)
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

def to_message(user_id: str, image_path: str, additional_info: str, quadkey: str = ""):
    return {'user_id': user_id,
                 'image_path': image_path,
                 'additional_info': additional_info,
                 'quadkey': quadkey}

@dp.message_handler(state=QStates.find, content_types=['photo'])
async def process_find(message: types.Message, state: FSMContext):
    additional_info = message.to_python().get("caption", "")
    id = str(uuid.uuid4())
    image_name = "{0}.jpg".format(id)
    os.makedirs("/tmp/data", exist_ok=True)
    image_path = os.path.join("/tmp/data", image_name)
    await message.photo[-1].download(image_path)
    kafka_message = to_message(message.from_user.id, image_path, additional_info)
    kafka_producer.send(value=kafka_message, key=id, topic='find_cat')
    await message.answer("Thanks! We notify you when we'll get any news")

@dp.message_handler(state=QStates.saw, content_types=['photo'])
async def process_saw(message: types.Message, state: FSMContext):
    additional_info = message.to_python().get("caption", "")
    id = str(uuid.uuid4())
    image_name = "{0}.jpg".format(id)
    os.makedirs("/tmp/data", exist_ok=True)
    image_path = os.path.join("/tmp/data", image_name)
    await message.photo[-1].download(image_path)
    kafka_message = to_message(message.from_user.id, image_path, additional_info)
    kafka_producer.send(value=kafka_message, key=id, topic='saw_cat')
    await message.answer("Thank you !!!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, timeout=10*60)