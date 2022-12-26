from aiogram.dispatcher.filters.state import StatesGroup, State


class RStates(StatesGroup):
    saw = State()
    find = State()
    geo = State()
    ask_name_contact = State()
    ask_extra_info = State()
    wait_extra_info = State()

    ask_search_new_cat = State()
