from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def appointment_time_keyboard(times):
    buttons = []
    for time in times:
        button = InlineKeyboardButton(text=time, callback_data=time)
        buttons.append([button])
    back = InlineKeyboardButton(text='Назад', callback_data='back_to_choose_date')
    buttons.append([back])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb