from time import sleep

import cv2
from telegram import Bot, InputMediaPhoto
from json import dumps
from src.entities.cat import ClosestCats
from src.telegram_bot.configs.bot_base_configs import S3ClientConfig
from src.utils.s3_client import YandexS3Client


class DataUploader:
    def __init__(self, token, s3_config: S3ClientConfig):
        self.bot = Bot(token)
        self.s3_client = YandexS3Client(
            s3_config.aws_access_key_id, s3_config.aws_secret_access_key
        )


    def upload(self, closest: ClosestCats):

        closest_cats_amount = len(closest.cats)
        self.bot.send_message(
            closest.person.chat_id, f"We found {closest_cats_amount} similar cats."
        )
        for cat_num, cat in enumerate(closest.cats):
            media_group = []
            self.bot.send_message(
                closest.person.chat_id, f"Cat {cat_num + 1} from {closest_cats_amount}."
            )
            for path in cat.paths:
                cat_image = self.s3_client.load_image(path)
                cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
                cat_image_bytes = cv2.imencode(".jpg", cat_image)[1].tobytes()
                media_group.append(InputMediaPhoto(media=cat_image_bytes))
            self.bot.send_media_group(chat_id=closest.person.chat_id, media=media_group)
            self.bot.send_message(closest.person.chat_id, cat.additional_info)


# @dp.message_handler(Text(equals="Unsubscribe", ignore_case=True))
# async def unsubscribe(message: types.Message, state: FSMContext, cache: CatsCache):
#     await message.answer(
#         "Your cats:", reply_markup=types.ReplyKeyboardRemove()
#     )
#    # person_cats = cats_cache.find_person_cats(message.from_user.id)
#     person_cats = cache.find_person_cats(message.from_user.id)
#     await message.answer(
#         f"you send us {len(person_cats)}"
#     )
#     for cat in person_cats:
#
#         await message.answer(
#             " ----- \n name: {0}, \n task: {1},\n comment: {2}\n -----".format(*cat)
#         )
