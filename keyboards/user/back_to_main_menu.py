from aiogram.utils.keyboard import ReplyKeyboardBuilder

def back_to_main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Вернуться в главное меню")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
