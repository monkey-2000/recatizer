import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import  FSMContext
from aiogram.types import ContentType
from dotenv import load_dotenv

from telegram_bot import keyboard

load_dotenv()
BOT_TOKEN = os.environ['BOT_TOKEN']
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


class NSTInput(StatesGroup):
    waiting_for_content = State()
    waiting_for_output = State()


@dp.message_handler(commands=['start'])
async def start_menu(message: types.Message):
    await message.answer(text='1',
                         reply_markup=keyboard.MENU)


@dp.message_handler(commands='find')
async def show_match_result(message: types.Message):
    ##
    await message.answer(text='This is your cat?',
                         reply_markup=keyboard.FIND)


@dp.message_handler(content_types=[ContentType.PHOTO, ContentType.DOCUMENT])
async def get_photo(message: types.Message):
    await message.photo[-1].download('ggg.jpg')
    #inference()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)