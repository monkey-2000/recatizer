from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from src.telegram_bot.bot_tools.menu_texts import saw_lost_menu_text
from src.telegram_bot.bot_tools.states import RStates


async def saw_cat(message: types.Message, state: FSMContext):
    await message.answer(saw_lost_menu_text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RStates.saw)
    await state.update_data(kafka_topic="saw_cat")


def register_saw_cat_handlers(dp: Dispatcher):
    dp.register_message_handler(
        saw_cat, Text(equals="saw cat", ignore_case=True), state="*"
    )
