from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.contact_button import contact_button
from keyboards.choose_step import all_steps_button
from keyboards.admin import admin_keyboard
from keyboards.time_appointment import time_keyboard
from keyboards.choose__type_delete import delete_type
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states import CreateAppointmentStep
from . import telegramcalendar
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
from aiogram import types
from models import AvailableTime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from secret import  db_connect
from aiogram.utils.keyboard import InlineKeyboardBuilder

Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


appointments = (
    session.query(AvailableTime)
    .order_by(
        AvailableTime.year,
        AvailableTime.month,
        AvailableTime.day,
        AvailableTime.time,
    )
    .all()
)


def time_keyboard():
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
    buttons = []
    for time in times:
        button = InlineKeyboardButton(text=time, callback_data=time)
        buttons.append([button])
    accept_button = InlineKeyboardButton(text="Подтвердить", callback_data="accept")
    buttons.append([accept_button])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb
