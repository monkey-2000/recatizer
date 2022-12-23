from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from src.telegram_bot.bot_tools.keyboards import get_main_menu_kb

MatchesCb = CallbackData("matches", "action", "cat_id")


async def mark_answer(call: types.CallbackQuery, callback_data: dict):
    cat_id = callback_data["cat_id"]
    await call.message.answer(text=cat_id, reply_markup=types.ReplyKeyboardRemove())


async def back_to_menu(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=False)

    keyboard = get_main_menu_kb()
    await call.message.answer(
        text='Hi',
        reply_markup=keyboard,
    )



def register_match_handlers(dp: Dispatcher):

    dp.register_callback_query_handler(
        mark_answer, MatchesCb.filter(action=["yes", "no"]), state="*"
    )
    dp.register_callback_query_handler(
        back_to_menu, MatchesCb.filter(action=["back"]), state="*"
    )
