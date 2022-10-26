from telegram import Bot, InputMediaPhoto
from json import dumps
from inference.entities.cat import ClosestCats


class DataUploader:
    def __init__(self, token):
        self.bot = Bot(token)

    def upload(self, closest: ClosestCats):
        media_group = []
        for cat in closest.cats:
            media_group.append(InputMediaPhoto(open(cat.path, "rb"), caption=dumps(cat.additional_info)))
        self.bot.send_media_group(chat_id=closest.person.chat_id,
                                  media=media_group)
