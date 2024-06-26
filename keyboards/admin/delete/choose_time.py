from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def time_delete_keyboard(times):
    buttons = []
    for time in times:
        button = InlineKeyboardButton(text=time, callback_data=time)
        buttons.append([button])
    accept_button = InlineKeyboardButton(text="Подтвердить", callback_data="accept")
    buttons.append([accept_button])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb
