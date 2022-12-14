from aiogram import types


# def get_callback_kb(wanted_cat_id, match_cat_id, callback ,action, text):
#
#     buttons = [
#         types.InlineKeyboardButton(
#             text=text, callback_data=callback.new(action=action, wanted_cat_id=wanted_cat_id, match_cat_id=match_cat_id)
#         ),
#     ]
#     keyboard = types.InlineKeyboardMarkup(row_width=1)
#     keyboard.add(*buttons)
#     return keyboard


def get_callback_kb(cat_id, callback ,action, text):

    buttons = [
        types.InlineKeyboardButton(
            text=text, callback_data=callback.new(action=action, cat_id=cat_id)
        ),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


