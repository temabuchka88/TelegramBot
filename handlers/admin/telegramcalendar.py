from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import datetime
import calendar
from .current_calendar import russian_month_names

# def create_callback_data(action, year, month, day):
#     """Create the callback data associated with each button"""
#     return ";".join([action, str(year), str(month), str(day)])

def create_callback_data(action, year=None, month=None, day=None):
    """Create the callback data associated with each button"""
    data = [action]
    if year is not None:
        data.append(str(year))
    if month is not None:
        data.append(str(month))
    if day is not None:
        data.append(str(day))
    return ";".join(data)

def separate_callback_data(data):
    """Separate the callback data"""
    return data.split(";")

def create_calendar(year=None, month=None):
    now = datetime.datetime.now()
    today = now.date()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = []
    # First row - Month and Year
    row = []
    row.append(
        InlineKeyboardButton(
            text=russian_month_names[month] + " " + str(year), callback_data=data_ignore
        )
    )
    keyboard.append(row)
    # Second row - Week Days
    row = []
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        row.append(InlineKeyboardButton(text=day, callback_data=data_ignore))
    keyboard.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data=data_ignore))
            else:
                date = datetime.date(year, month, day)
                if date < today:
                    row.append(InlineKeyboardButton(text="-", callback_data=data_ignore))
                else:
                    row.append(
                        InlineKeyboardButton(
                            text=str(day),
                            callback_data=create_callback_data("DAY", year, month, day),
                        )
                    )
        keyboard.append(row)
    # Last row - Buttons
    row = []
    row.append(
        InlineKeyboardButton(
            text="<", callback_data=create_callback_data("PREV-MONTH", year, month, 1)
        )
    )
    row.append(InlineKeyboardButton(text="Подтвердить", callback_data="accept"))
    row.append(
        InlineKeyboardButton(
            text=">", callback_data=create_callback_data("NEXT-MONTH", year, month, 1)
        )
    )
    keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
