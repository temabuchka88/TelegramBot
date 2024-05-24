from aiogram.utils.keyboard import ReplyKeyboardBuilder

def all_steps_button():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Записаться")
    kb.button(text="Адрес")
    kb.button(text="Мой профиль")
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True)
