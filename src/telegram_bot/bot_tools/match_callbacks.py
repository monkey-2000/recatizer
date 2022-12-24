from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from bson import ObjectId

from src.services.user_profile_service import UserProfileClient
from src.telegram_bot.bot_tools.keyboards import get_main_menu_kb
from src.telegram_bot.bot_tools.main_menu_text import start_menu_text
from src.telegram_bot.configs.bot_cfgs import bot_config

user_profile = UserProfileClient(bot_config)
MatchesCb = CallbackData("matches", "action", "match_id")


async def mark_answer(call: types.CallbackQuery, callback_data: dict):
    match_id = callback_data["match_id"]
    answer = user_profile.answers_db.find({'_id': ObjectId(match_id)})[0]
    if callback_data["action"] == "yes":
        answer.user_answer = 1
    elif callback_data["action"] == "no":
        answer.user_answer = 0
    user_profile.answers_db.update(answer)
    await call.answer(text="We mark your answer!", show_alert=True)


def register_match_handlers(dp: Dispatcher):

    dp.register_callback_query_handler(
        mark_answer, MatchesCb.filter(action=["yes", "no"]), state="*"
    )


