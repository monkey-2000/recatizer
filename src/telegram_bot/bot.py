import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand

from src.telegram_bot.bot_tools.commands_handlers import register_commands_handlers
from src.telegram_bot.bot_tools.find_cat_handlers import register_find_cat_handlers
from src.telegram_bot.bot_tools.keyboards import get_main_menu_kb
from src.telegram_bot.bot_tools.main_menu_text import start_menu_text
from src.telegram_bot.bot_tools.match_callbacks import register_match_handlers
from src.telegram_bot.bot_tools.save_new_cat_handlers import register_save_new_cat_handlers
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
    commands = [BotCommand(command='/start', description="go to main menu"),
                BotCommand(command='/help', description="show help")]
                # BotCommand(command='/my_cat', description="show my cats")]
    await bot.set_my_commands(commands)



# @dp.message_handler(commands=["start"], state="*")
# async def start(message: types.Message, state: FSMContext):
#     await state.reset_state(with_data=False)
#     keyboard = get_main_menu_kb()
#     await message.answer(
#         text=start_menu_text,
#         reply_markup=keyboard,
#     )
#
#
# @dp.message_handler(commands=['help'], state="*")
# async def show_matches(message: types.Message, state: FSMContext):
#     await message.answer(f'You value is ')



async def main():
    await set_commands(bot)
    await dp.skip_updates()
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())



