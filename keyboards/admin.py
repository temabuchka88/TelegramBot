from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def admin_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(
        types.KeyboardButton(text="Добавить запись"),
        types.KeyboardButton(text="Удалить запись"),
        types.KeyboardButton(text="Все записи"),
    )
    kb.row(types.KeyboardButton(text="Вернуться в главное меню"))
    return kb.as_markup(resize_keyboard=True)
