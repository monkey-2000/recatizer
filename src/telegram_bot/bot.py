import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from src.telegram_bot.bot_tools.commands_handlers import register_commands_handlers
from src.telegram_bot.bot_tools.find_cat_handlers import register_find_cat_handlers
from src.telegram_bot.bot_tools.match_callbacks import register_match_handlers
from src.telegram_bot.bot_tools.save_new_cat_handlers import (
    register_save_new_cat_handlers,
)
from src.telegram_bot.bot_tools.saw_cat_handlers import register_saw_cat_handlers
from src.telegram_bot.configs.bot_cfgs import bot_config
from src.telegram_bot.middleware import AlbumMiddleware


storage = MemoryStorage()
bot = Bot(token=bot_config.token)

dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(AlbumMiddleware())

register_find_cat_handlers(dp)
register_saw_cat_handlers(dp)
register_match_handlers(dp)
register_save_new_cat_handlers(dp)
register_commands_handlers(dp)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="go to main menu"),
        BotCommand(command="/help", description="show help"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await set_commands(bot)
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
