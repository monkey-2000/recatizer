from aiogram import types, Dispatcher
from aiogram.utils.callback_data import CallbackData
from bson import ObjectId


from src.telegram_bot.bot_tools.user_profile_service import UserProfileClient
from src.telegram_bot.configs.bot_cfgs import bot_config

user_profile = UserProfileClient(bot_config)
MatchesCb = CallbackData("matches", "action", "match_id")


async def mark_answer(call: types.CallbackQuery, callback_data: dict):
    match_id = callback_data["match_id"]
    answer = user_profile.answers_db.find({"_id": ObjectId(match_id)})[0]
    if callback_data["action"] == "yes":
        answer.user_answer = 1
    elif callback_data["action"] == "no":
        answer.user_answer = 0
    user_profile.answers_db.update(answer)
    await call.answer(text="We mark your answer!", show_alert=True)


async def show_more_about_cat(call: types.CallbackQuery, callback_data: dict):
    match_id = callback_data["match_id"]
    await user_profile.send_match_with_extra(call.message, match_id)
    await call.answer()


def register_match_handlers(dp: Dispatcher):

    dp.register_callback_query_handler(
        mark_answer, MatchesCb.filter(action=["yes", "no"]), state="*"
    )

    dp.register_callback_query_handler(
        show_more_about_cat, MatchesCb.filter(action=["show_more_info"]), state="*"
    )
