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
from secret import  db_connect
router = Router()

Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# добавить или step choose step через fsm
@router.message(F.text == "Вернуться в главное меню")
async def show_main_menu(message: Message):
    await message.answer("Выберите действие:", reply_markup=all_steps_button())
