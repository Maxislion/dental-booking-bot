from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Записаться")],
            [KeyboardButton(text="💰 Услуги и цены")]
        ],
        resize_keyboard=True
    )