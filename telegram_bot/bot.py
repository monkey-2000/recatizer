import json
import logging
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


from kafka import KafkaProducer


class Producer:
    def __init__(self, bootstrap_servers=['localhost:9092']):
            self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                                    value_serializer=lambda v: json.dumps(v).encode('ascii'),
                                    key_serializer=lambda v: json.dumps(v).encode('ascii'))

    def send(self, value, key):
        self.producer.send('find_cat',
              key={'id': key},
              value=value
             )
        self.producer.flush()
        return True

load_dotenv()
BOT_TOKEN = os.environ['BOT_TOKEN']
bot = Bot(token=BOT_TOKEN)
loop = asyncio.get_event_loop()
dp = Dispatcher(bot, loop=loop)

CNT = 0
logger = logging.getLogger('chat_bot_logger')
async def _inference(msg):
    global logger, CNT
    CNT += 1
    loc_cnt = CNT
    loc_cnt += 1

    #logger.debug(f"запрос find начало{loc_cnt}")
    print(f"запрос find начало{loc_cnt}")
    #await asyncio.sleep(30)
    sleep(5 * 60)
    #logger.debug(f"запрос find конец{loc_cnt}")
    print(f"запрос find конец{loc_cnt}")
    return '/home/art/PycharmProjects/recatizer/app/images/2022-10-04 23.34.11.jpg'
async def _inference_1(msg):
    global logger, CNT
    CNT += 1
    loc_cnt = CNT
    loc_cnt += 1
    print(f"запрос find начало{loc_cnt}")
    sleep(5 * 60)
    print(f"запрос find конец{loc_cnt}")
    return '/home/art/PycharmProjects/recatizer/app/images/2022-10-04 23.34.11.jpg'
# @dp.message_handler(commands=['start'])
# async def start_menu(message: types.Message):
#     await message.answer(text='1',
#                          reply_markup=keyboard.MENU)


# @dp.message_handler(commands='find')
# async def show_match_result(message: types.Message):
#     ##
#     await message.answer(text='This is your cat?',
#                          reply_markup=keyboard.FIND)


#@dp.message_handler(content_types=[ContentType.PHOTO, ContentType.DOCUMENT])
@dp.message_handler(commands='find')
async def get_photo(message: types.Message):
    global CNT
    CNT += 1
    loc_cnt = CNT
    loc_cnt += 1

    answer_dir = f'/home/art/PycharmProjects/recatizer/telegram_bot/res_cat/{loc_cnt}/'

    sender = Producer()
    kafka_msg = {'name': message.from_user.id,
                 'breez': 'xxx',
                 'img_path': '...img',
                 'geo': 111,
                 'answer_dir': answer_dir}
    sender.send(value=kafka_msg, key=loc_cnt)

    os.mkdir(answer_dir)
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





    #inference()



if __name__ == '__main__':
    logger.setLevel('INFO')
    fh = logging.FileHandler('SPOT.log')
    fh.setLevel(level=logging.DEBUG)
    fh.setLevel(level=logging.DEBUG)
    logger.addHandler(fh)
    logger.setLevel(level=logging.INFO)
    logger.debug("Бот запущен.")

    executor.start_polling(dp, skip_updates=True, timeout=10*60)