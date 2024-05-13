from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import calendar
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.contact_button import contact_button
from keyboards.choose_step import all_steps_button

from states import RegistrationStep

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    create_engine,
    select,
    text,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from sqlalchemy import Column, Integer, Date, ARRAY, Time
from models import AvailableTime
from secret import  db_connect

Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
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
    """Create the callback data associated with each button"""
    return ";".join([action, str(year), str(month), str(day)])


def separate_callback_data(data):
    """Separate the callback data"""
    return data.split(";")


def get_dates_with_appointments():
    """Get all dates with appointments from the database"""
    session = Session()
    try:
        dates = session.query(AvailableTime.date.distinct()).all()
        return [date[0] for date in dates]
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()

def create_current_calendar(year=None, month=None):
    """Create a calendar with dates from the database"""
    dates_with_appointments = get_dates_with_appointments()
    now = datetime.now()
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
                row.append(InlineKeyboardButton(text=" - ", callback_data=data_ignore))
            else:
                date = datetime(year, month, day).date()
                if date in dates_with_appointments:
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
    # Last row - Buttons
    row = []
    row.append(
        InlineKeyboardButton(
            text="<", callback_data=create_callback_data("PREV-MONTH", year, month, 1)
        )
    )
    # row.append(InlineKeyboardButton(text=" ", callback_data=data_ignore))
    row.append(
        InlineKeyboardButton(
            text=">", callback_data=create_callback_data("NEXT-MONTH", year, month, 1)
        )
    )
    keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
