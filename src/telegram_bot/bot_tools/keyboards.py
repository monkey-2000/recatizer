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

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2,  one_time_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(text="SAW CAT"))
    buttons.append(types.KeyboardButton(text="LOST CAT"))
    # buttons.append(types.KeyboardButton(text="My subscriptions"))
    # buttons.append(types.KeyboardButton(text="My matches"))
    keyboard.add(*buttons)
    return keyboard

def get_match_kb():
    buttons = [
        types.InlineKeyboardButton(
            text="\U0000274c", callback_data=self.MatchesCb.new(action="no", cat_id=cat._id)
        ),
        types.InlineKeyboardButton(
            text="My \U0001F638", callback_data=self.MatchesCb.new(action="yes", cat_id=cat._id)
        ),
        types.InlineKeyboardButton(
            text="\U00002b05", callback_data=self.MatchesCb.new(action="back", cat_id=cat._id)
        ),
        types.InlineKeyboardButton(
            text="\U00002705 I find my cat", callback_data=self.MatchesCb.new(action="find", cat_id=cat._id)
        ),

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)

