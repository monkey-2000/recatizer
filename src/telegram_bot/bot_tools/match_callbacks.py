from aiogram import types, Dispatcher
from aiogram.utils.callback_data import CallbackData
from bson import ObjectId


from src.telegram_bot.bot_tools.user_profile_service import UserProfileClient
from src.telegram_bot.configs.bot_cfgs import bot_config

user_profile = UserProfileClient(bot_config)
MatchesCb = CallbackData("matches", "action", "match_id")


async def mark_answer(call: types.CallbackQuery, callback_data: dict):
    cat_id = callback_data["match_id"]
    cat = user_profile.cats_db.find({"_id": ObjectId(cat_id)})[0]
    chat_id = call.from_user.id
    if not user_profile.exists_match(chat_id=chat_id,
                                     cat=cat):
        await call.answer(text="This match has already been noted!", show_alert=True)
        return

    if callback_data["action"] == "yes":
        wanted_cat = user_profile.cats_db.find({"chat_id": chat_id,
                                                "is_active": True})[0]

        user_profile.answers_db.save_correct_answer(wanted_cat=wanted_cat._id,
                                                    cat_id=cat._id)
    elif callback_data["action"] == "no":

        user_profile.delete_match(chat_id=chat_id,
                                  cat=cat)
        # TODO fix case with no cat
    await call.answer(text="We mark your answer!", show_alert=True)


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