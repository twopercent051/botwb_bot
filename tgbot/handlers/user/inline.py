from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class InlineKeyboard:

    def __init__(self):
        pass

    @staticmethod
    def chat_following_kb():
        keyboard = [[
            InlineKeyboardButton(text="Подписаться на канал", url="https://t.me/+6dRLrSfmefhhODRi"),
            InlineKeyboardButton(text="Я подписался", callback_data="Я подписался"),
        ]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def item_subscribe_kb(article: int | str):
        keyboard = [[InlineKeyboardButton(text="🔘 Включить отслеживание", callback_data=f"subscribe:{article}")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def item_subscribe_off_kb(article: int | str):
        keyboard = [[InlineKeyboardButton(text="➖ Выключить отслеживание", callback_data=f"subscribe_off:{article}")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
