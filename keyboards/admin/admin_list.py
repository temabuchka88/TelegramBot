from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def admin_list_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(
        types.KeyboardButton(text="Добавить администратора"),
        types.KeyboardButton(text="Удалить администратора"),
    )
    kb.row(types.KeyboardButton(text="Назад"))
    return kb.as_markup(resize_keyboard=True)
