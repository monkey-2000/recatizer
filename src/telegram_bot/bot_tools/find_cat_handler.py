from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.callback_data import CallbackData

from src.services.user_profile_service import UserProfileClient
from src.telegram_bot.bot_tools.keyboards import get_main_menu_kb
from src.telegram_bot.bot_tools.main_menu_text import start_menu_text
from src.telegram_bot.bot_tools.states import RStates
from src.telegram_bot.configs.bot_cfgs import bot_config

user_profile = UserProfileClient(bot_config)
FindCb = CallbackData("matches", "action")

async def lost_cat(message: types.Message, state: FSMContext):
    query = {"chat_id": message.from_user.id, "is_active": True}
    cats = user_profile.people_db.find(query)
    await state.set_state(RStates.find)
    if len(cats) > 0:
        await message.answer("You are already looking for. What do You want?",
                             reply_markup=get_find_kb())
    else:
        await message.answer(
            "Please upload photo of your cat", reply_markup=types.ReplyKeyboardRemove()
        )

        await state.update_data(kafka_topic="find_cat")


async def back_to_menu(call: types.CallbackQuery, state: FSMContext):

    await state.finish()
    await call.message.answer(
        text=start_menu_text,
        reply_markup=get_main_menu_kb(),
    )
    await call.answer()
    # await call.message.delete_message(call.message.chat.id, call.message.message_id)


async def show_last_matches(call: types.CallbackQuery, state: FSMContext):
    # await state.reset_state(with_data=False)

    query = {"chat_id": call.from_user.id, "is_active": True}
    wanted_cat = user_profile.people_db.find(query)
    query = {"wanted_cat_id": wanted_cat[0]._id, "user_answer": -1}
    matches = user_profile.answers_db.find(query)
    for match in matches:
        query = {"_id": match.match_cat_id, "is_active": True}
        cat = user_profile.cats_db.find(query)
        await user_profile.send_match(call.message, *cat)


async def unsubscribe_from_wanted_cat(call: types.CallbackQuery, state: FSMContext):

    # await state.reset_state(with_data=False)
    query = {"chat_id": call.from_user.id, "is_active": True}
    wanted_cats = user_profile.people_db.find(query)

    for cat in wanted_cats:
        cat.is_active = False
        user_profile.people_db.update(cat)
    await state.finish()
    await call.message.answer(text=start_menu_text,
                      reply_markup=get_main_menu_kb())
    await call.answer(text="We deleted your cat!", show_alert=True)
    # await call.message.delete_message(call.message.chat.id, call.message.message_id)




def get_find_kb():
        buttons = [
            types.InlineKeyboardButton(
                text="\U00002b05", callback_data=FindCb.new(action="back")
            ),
            types.InlineKeyboardButton(
                text="show \U0001F638\U0001F638\U0001F638", callback_data=FindCb.new(action="show")
            ),
            types.InlineKeyboardButton(
                text="\U00002705 I find my cat", callback_data=FindCb.new(action="unsubscribe")
            ),

        ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        return keyboard



def register_find_cat_handlers(dp: Dispatcher):
    dp.register_message_handler(
        lost_cat, Text(equals="I lost my cat", ignore_case=True), state="*")

    dp.register_callback_query_handler(
        back_to_menu, FindCb.filter(action=["back"]), state="*")
    dp.register_callback_query_handler(
        show_last_matches, FindCb.filter(action=["show"]), state="*")
    dp.register_callback_query_handler(
        unsubscribe_from_wanted_cat, FindCb.filter(action=["unsubscribe"]), state="*")