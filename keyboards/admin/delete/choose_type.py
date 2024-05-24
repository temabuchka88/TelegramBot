from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def delete_type():
    buttons = []
    b1 = InlineKeyboardButton(text="Удалить весь день", callback_data="delete_full_day")
    b2 = InlineKeyboardButton(
        text="Удалить конкретную запись", callback_data="delete_time"
    )
    buttons.append([b1])
    buttons.append([b2])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb
