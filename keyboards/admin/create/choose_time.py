import json
import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

initial_times = {
    "times": [
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
        "20:00"
    ]
}

def create_times_file():
    with open('times.json', 'w', encoding='utf-8') as f:
        json.dump(initial_times, f, ensure_ascii=False, indent=4)

def load_times():
    if not os.path.exists('times.json'):
        create_times_file()

    with open('times.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data["times"]

def time_keyboard():
    times = load_times()
    buttons = []
    for time in times:
        button = InlineKeyboardButton(text=time, callback_data=time)
        buttons.append([button])
    accept_button = InlineKeyboardButton(text="Подтвердить", callback_data="accept")
    buttons.append([accept_button])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb


def add_time(new_time):
    with open('times.json', 'r+', encoding='utf-8') as f:
        data = json.load(f)
        if new_time not in data["times"]:
            data["times"].append(new_time)
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()

