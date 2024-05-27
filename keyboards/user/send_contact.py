from aiogram.utils.keyboard import ReplyKeyboardBuilder


def contact_button():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Поделиться контактом", request_contact=True)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
