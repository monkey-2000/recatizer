from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from src.telegram_bot.bot_tools.keyboards import get_main_menu_kb
from src.telegram_bot.bot_tools.main_menu_text import start_menu_text, help_text


async def start(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    keyboard = get_main_menu_kb()
    await message.answer(
        text=start_menu_text,
        reply_markup=keyboard,
    )



async def help(message: types.Message):
    await message.answer(
        text=help_text
    )

def register_commands_handlers(dp: Dispatcher):


    dp.register_message_handler(start, commands=["start"], state="*")

    dp.register_message_handler(help, commands=['help'], state="*")
