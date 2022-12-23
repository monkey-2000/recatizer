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


def get_main_menu_kb():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = []
    buttons.append(types.KeyboardButton(text="I saw a cat"))
    buttons.append(types.KeyboardButton(text="I lost my cat"))
    # buttons.append(types.KeyboardButton(text="My subscriptions"))
    # buttons.append(types.KeyboardButton(text="My matches"))
    keyboard.add(*buttons)
    return keyboard


