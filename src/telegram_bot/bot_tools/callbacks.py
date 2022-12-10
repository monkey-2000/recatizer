from aiogram import  types
from contextlib import suppress

from aiogram.utils.exceptions import MessageNotModified
from telebot.callback_data import CallbackData

UnsubscribeCb = CallbackData("cats", "action", "cat_id")

class UnsubscribeCats():

    def __init__(self):
        pass

    def get_keyboard_cat(self, cat_id, action="unsubsscribe"):

        if action == "unsubsscribe":
            text = "Unsubscribe"
        else:
            text = "Subscribe"

        buttons = [
            types.InlineKeyboardButton(text=text, callback_data=UnsubscribeCb.new(
                                                                        action=action,
                                                                        cat_id=cat_id)),
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        return keyboard

    async def update_num_text_fab(self, message: types.Message, action: str, cat_id: str):
        with suppress(MessageNotModified):
            await message.edit_reply_markup(reply_markup=self.get_keyboard_cat(action=action, cat_id=cat_id))

@dp.callback_query_handler(UnsubscribeCb.filter(action=["unsubsscribe"]))
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    cat_id = callback_data["cat_id"]
    await update_num_text_fab(call.message, action="subsscribe", cat_id=cat_id)
    await call.answer(text='You Unsubsscribed')

@dp.callback_query_handler(UnsubscribeCb.filter(action=["subsscribe"]))
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    cat_id = callback_data["cat_id"]
    await update_num_text_fab(call.message, action="unsubsscribe", cat_id=cat_id)
    await call.answer(text='You Subsscribed')