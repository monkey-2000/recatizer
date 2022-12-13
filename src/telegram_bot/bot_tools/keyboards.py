from aiogram import types


def get_callback_kb(cat_id, callback ,action, text):

    buttons = [
        types.InlineKeyboardButton(
            text=text, callback_data=callback.new(action=action, cat_id=cat_id)
        ),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard





