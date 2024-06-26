from aiogram.utils.keyboard import ReplyKeyboardBuilder

def cancel_appointment():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Отменить запись")
    kb.button(text="Вернуться в главное меню")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)