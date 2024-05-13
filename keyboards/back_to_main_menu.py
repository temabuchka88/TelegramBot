from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def back_to_main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Вернуться в главное меню")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
