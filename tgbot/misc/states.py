from aiogram.fsm.state import State, StatesGroup


class UserFSM(StatesGroup):
    home = State()
    get_kw = State()
    get_article = State()