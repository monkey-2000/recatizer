from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

BTN_FIND= InlineKeyboardButton('Find', callback_data='find')
BTN_SAW = InlineKeyboardButton('Saw', callback_data='saw')
BTN_MENU = InlineKeyboardButton('Menu', callback_data='menu')

FIND = InlineKeyboardMarkup().add(BTN_MENU)
SAW = InlineKeyboardMarkup().add(BTN_MENU)
MENU = InlineKeyboardMarkup().add(BTN_FIND, BTN_SAW)