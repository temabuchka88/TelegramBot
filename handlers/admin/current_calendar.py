from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import calendar
from datetime import datetime
from models import AvailableTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from secret import  db_connect

connection_string = db_connect
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

russian_month_names = [
    "",
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]


def create_callback_data(action, year, month, day):
    return ";".join([action, str(year), str(month), str(day)])


def separate_callback_data(data):
    return data.split(";")


def get_dates_with_appointments():
    session = Session()
    try:
        dates = session.query(AvailableTime.date.distinct()).all()
        return [date[0] for date in dates]
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()


def create_current_calendar(year=None, month=None):
    dates_with_appointments = get_dates_with_appointments()
    now = datetime.now()
    today = now.date()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = []
    row = []
    row.append(
        InlineKeyboardButton(
            text=russian_month_names[month] + " " + str(year), callback_data=data_ignore
        )
    )
    keyboard.append(row)
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
                date = datetime(year, month, day).date()
                if date < today:
                    row.append(InlineKeyboardButton(text=" - ", callback_data=data_ignore))
                elif date == today:
                    row.append(InlineKeyboardButton(text="-", callback_data=data_ignore))
                elif date in dates_with_appointments:
                    row.append(
                        InlineKeyboardButton(
                            text=str(day),
                            callback_data=create_callback_data("DAY", year, month, day),
                        )
                    )
                else:
                    row.append(
                        InlineKeyboardButton(text=" - ", callback_data=data_ignore)
                    )
        keyboard.append(row)
    row = []
    row.append(
        InlineKeyboardButton(
            text="<", callback_data=create_callback_data("PREV-MONTH", year, month, 1)
        )
    )
    row.append(
        InlineKeyboardButton(
            text=">", callback_data=create_callback_data("NEXT-MONTH", year, month, 1)
        )
    )
    keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
