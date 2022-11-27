import asyncio
import uuid
from typing import List, Union

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups.
    [https://github.com/WhiteMemory99/aiogram_album_handler/blob/master/example/album.py]"""

    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id and len(message.photo) == 0:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element

        except KeyError:
            if message.media_group_id:
                self.album_data[message.media_group_id] = [message]
                data["album"] = self.album_data[message.media_group_id]

            elif len(message.photo) > 0:
                data["album"] = [message]

            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["cat_name"] = str(uuid.uuid4())

    async def on_post_process_message(
        self, message: types.Message, result: dict, data: dict
    ):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]
