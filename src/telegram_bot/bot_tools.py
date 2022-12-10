import types
from typing import Optional

from aiogram.utils.callback_data import CallbackData




# class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
#     action: str
#     value: Optional[int]

cb= CallbackData("id", "action")
def get_keyboard_fab(cat_id):

    buttons = [
        types.InlineKeyboardButton(text="Unsubscribe", callback_data=cb.new(action="unsubsscribe",
                                                                     cat_id=cat_id)),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard.as_markup()


# @dp.callback_query_handler(cb.filter(action=["unsubsscribe"]))
# async def callbacks(call: types.CallbackQuery, callback_data: dict):
#     cat_id = callback_data["cat_id"]
#     print(f'отписка от котика {cat_id}')
