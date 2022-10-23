import os
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import  FSMContext
from aiogram.types import ContentType
from dotenv import load_dotenv

#from telegram_bot import keyboard

from time import sleep

# from telegram_bot.queu.producer import Producer
from telegram_bot.queu.producer import Producer

load_dotenv()
BOT_TOKEN = os.environ['BOT_TOKEN']
bot = Bot(token=BOT_TOKEN)
loop = asyncio.get_event_loop()
dp = Dispatcher(bot, loop=loop)

CNT_FIND = 0 ## id
FIND_ANSWER_DIR = f'/home/art/PycharmProjects/recatizer/telegram_bot/res_cat/find_cat/'

CNT_SAW = 0
SAW_ANSWER_DIR = f'/home/art/PycharmProjects/recatizer/telegram_bot/res_cat/saw_cat/'
#logger = logging.getLogger('chat_bot_logger')

@dp.message_handler(commands='saw')
async def get_photo(message: types.Message):
    global CNT_SAW
    CNT_SAW += 1
    loc_cnt = CNT_FIND
    loc_cnt += 1

    answer_dir = SAW_ANSWER_DIR+ f'{loc_cnt}/'
    sender = Producer()
    kafka_msg = {'name': message.from_user.id,
                 'breez': 'xxx',
                 'img_path': '...img',
                 'geo': 111,
                 'answer_dir': answer_dir}
    sender.send(value=kafka_msg, key=loc_cnt, topic='saw_cat')
    os.makedirs(answer_dir)
    # отправка ответа о получении

@dp.message_handler(commands='find')
async def get_photo(message: types.Message):
    global CNT_FIND
    CNT_FIND += 1
    loc_cnt = CNT_FIND
    loc_cnt += 1

    answer_dir = FIND_ANSWER_DIR + f'{loc_cnt}/'

    sender = Producer()
    kafka_msg = {'name': message.from_user.id,
                 'breez': 'xxx',
                 'img_path': '...img',
                 'geo': 111,
                 'answer_dir': answer_dir}
    os.makedirs(answer_dir)

    sender.send(value=kafka_msg, key=loc_cnt, topic='find_cat')


    print(f'начало запроса {loc_cnt}')
    while len(os.listdir(answer_dir)) == 0:
        print('пока пусто')
        await asyncio.sleep(30)
        print(f'проверка {answer_dir}, результат {len(os.listdir(answer_dir))}')

    for img_path in os.listdir(answer_dir):
        print(answer_dir + img_path)
        with open(answer_dir + img_path, "rb") as f:
            photo = f.read()
            await bot.send_photo(message.from_user.id, photo)


if __name__ == '__main__':
    # Need to find way how to logging in acinc function!!!
    # logger.setLevel('INFO')
    # fh = logging.FileHandler('SPOT.log')
    # fh.setLevel(level=logging.DEBUG)
    # fh.setLevel(level=logging.DEBUG)
    # logger.addHandler(fh)
    # logger.setLevel(level=logging.INFO)
    # logger.debug("Бот запущен.")
    executor.start_polling(dp, skip_updates=True, timeout=10*60)