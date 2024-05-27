from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def appointment_time_keyboard(times):
    buttons = []
    for time in times:
        button = InlineKeyboardButton(text=time, callback_data=time)
        buttons.append([button])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb