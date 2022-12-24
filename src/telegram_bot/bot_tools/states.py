from aiogram.dispatcher.filters.state import StatesGroup, State


class RStates(StatesGroup):
    saw = State()
    find = State()
    geo = State()
    ask_extra_info = State()