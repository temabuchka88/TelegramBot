import json
import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

times = [
        "9:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
        "20:00",
    ]


def time_keyboard():
    buttons = []
    for time in times:
        button = InlineKeyboardButton(text=time, callback_data=time)
        buttons.append([button])
    accept_button = InlineKeyboardButton(text="Подтвердить", callback_data="accept")
    custom_time_button = InlineKeyboardButton(text="Другое время", callback_data="custom_time")
    buttons.append([custom_time_button])
    buttons.append([accept_button])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb


