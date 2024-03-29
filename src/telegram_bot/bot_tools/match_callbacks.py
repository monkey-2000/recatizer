from aiogram import types, Dispatcher
from aiogram.utils.callback_data import CallbackData
from bson import ObjectId


from src.telegram_bot.bot_tools.user_profile_service import UserProfileClient
from src.telegram_bot.configs.bot_cfgs import bot_config

user_profile = UserProfileClient(bot_config)
MatchesCb = CallbackData("matches", "action", "match_id")


async def mark_answer(call: types.CallbackQuery, callback_data: dict):
    cat_id = callback_data["match_id"]
    chat_id = call.from_user.id

    if not user_profile.exists_match(chat_id=chat_id,
                                     cat_id=cat_id):
        await call.answer(text="This match has already been noted!", show_alert=True)
        return

    if callback_data["action"] == "yes":
        user_profile.mark_answer(chat_id, cat_id, answer=1)

    elif callback_data["action"] == "no":
        user_profile.delete_match(chat_id=chat_id,
                                  cat_id=cat_id)
        user_profile.mark_answer(chat_id, cat_id, answer=0)

    await call.answer(text="We mark your answer!", show_alert=True)



# MAke it via kafka
async def show_more_about_cat(call: types.CallbackQuery, callback_data: dict):
    match_id = callback_data["match_id"]
    await call.answer(text="We send you more info.", show_alert=True)
    await user_profile.send_match_with_extra(call.message, match_id)



def register_match_handlers(dp: Dispatcher):

    dp.register_callback_query_handler(
        mark_answer, MatchesCb.filter(action=["yes", "no"]), state="*"
    )

    dp.register_callback_query_handler(
        show_more_about_cat, MatchesCb.filter(action=["show_more_info"]), state="*"
    )
