from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.contact_button import contact_button
from keyboards.choose_step import all_steps_button
from keyboards.back_to_main_menu import back_to_main_menu

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
from models import User, AvailableTime, Appointment

# from asd import GoogleCalendar
import calendar as std_calendar
from datetime import datetime

from aiogram_calendar import (
    SimpleCalendar,
    SimpleCalendarCallback,
    DialogCalendar,
    DialogCalendarCallback,
    get_user_locale,
)
import logging
import asyncio
import sys
from datetime import datetime
import time
from keyboards.time_appointment import time_keyboard
from aiogram_calendar import (
    SimpleCalendar,
    SimpleCalendarCallback,
    DialogCalendar,
    DialogCalendarCallback,
    get_user_locale,
)
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.utils.markdown import hbold
from . import telegramcalendar
from aiogram import types
from . import current_calendar
from states import AppointmentStep
router = Router()
from keyboards.appointment_time import appointment_time_keyboard
from secret import  db_connect
Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@router.message(F.text == "Записаться")
async def start_command(message: Message, state: FSMContext):
    await message.reply(
        "Выберите дату: ", reply_markup=current_calendar.create_current_calendar()
    )
    await state.set_state(AppointmentStep.choose_date)

@router.callback_query(AppointmentStep.choose_date)
async def delete_select_day(callback: types.CallbackQuery, state: FSMContext):
    session = Session()
    try:
        data = current_calendar.separate_callback_data(callback.data)
        if data[0] == "DAY":
            year, month, day = map(int, data[1:])
            date = datetime(year, month, day).date()
            appointment = (
                session.query(AvailableTime).filter(AvailableTime.date == date).first()
            )
            if appointment:
                times = appointment.times
                formatted_times = [time.strftime("%H:%M") for time in times]
                await state.update_data(
                    year=year, month=month, day=day, times=formatted_times
                )
                await callback.message.edit_text(
                    "Выберите время: ",
                    reply_markup=appointment_time_keyboard(formatted_times),
                )
                await state.set_state(AppointmentStep.confirm_booking)
            else:
                await callback.message.edit_text("На выбранную дату записей нет.")
        else:
            await callback.message.edit_text("Ошибка выбора даты.")
            await state.set_state(AppointmentStep.choose_date)
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()

@router.callback_query(AppointmentStep.confirm_booking)
async def delete_selected_time(callback: types.CallbackQuery, state: FSMContext):
    session = Session()
    try:
        data = await state.get_data()
        time_obj = time.strptime(callback.data, '%H:%M')
        appointment_date = datetime(data["year"], data["month"], data["day"], time_obj.tm_hour,time_obj.tm_min)
        user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()
        print(user)
        appointment = Appointment(appointment_date = appointment_date, user_id=user.id)
        session.add(appointment)
        session.commit()
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()