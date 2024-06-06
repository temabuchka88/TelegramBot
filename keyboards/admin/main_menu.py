from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def admin_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(
        types.KeyboardButton(text="Добавить запись"),
        types.KeyboardButton(text="Удалить запись"),
        types.KeyboardButton(text="Активные записи"),
    )
    kb.row(
        types.KeyboardButton(text="Свободные окошки"),
        types.KeyboardButton(text="Прошлые записи записи"),
        types.KeyboardButton(text="Список пользователей"),
    )
    kb.row(types.KeyboardButton(text="Выйти из админ панели"))
    return kb.as_markup(resize_keyboard=True)
