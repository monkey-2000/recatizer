import logging
import os
import asyncio

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


async def _inference(msg):

    return '/home/art/PycharmProjects/recatizer/app/images/2022-10-04 23.34.11.jpg'

@dp.message_handler(commands=['start'])
async def start_menu(message: types.Message):
    await message.answer(text='1',
                         reply_markup=keyboard.MENU)


# @dp.message_handler(commands='find')
# async def show_match_result(message: types.Message):
#     ##
#     await message.answer(text='This is your cat?',
#                          reply_markup=keyboard.FIND)


@dp.message_handler(content_types=[ContentType.PHOTO, ContentType.DOCUMENT])
async def get_photo(message: types.Message):
    path = 'ggg.jpg'
    await message.photo[-1].download(path)
    msg = {'path': path}
    match = await _inference(msg)
    photo = open(match, "rb")
    await bot.send_photo(message.from_user.id, photo)
    #inference()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)