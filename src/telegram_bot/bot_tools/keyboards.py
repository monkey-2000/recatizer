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


def get_main_menu_kb():

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2,  one_time_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(text="SAW CAT"))
    buttons.append(types.KeyboardButton(text="LOST CAT"))
    # buttons.append(types.KeyboardButton(text="My subscriptions"))
    # buttons.append(types.KeyboardButton(text="My matches"))
    keyboard.add(*buttons)
    return keyboard


def get_extra_info_kb():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(text="Yes"))
    buttons.append(types.KeyboardButton(text="No"))
    keyboard.add(*buttons)
    return keyboard
def get_share_location_kb():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(text="Yes", request_location=True))
    buttons.append(types.KeyboardButton(text="No"))
    keyboard.add(*buttons)
    return keyboard

def ask_search_new_cat_kb():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(text="Yes"))
    buttons.append(types.KeyboardButton(text="No"))
    keyboard.add(*buttons)
    return keyboard