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

# Base = declarative_base()
# connection_string = db_connect
# engine = create_engine(connection_string)

# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
# # session = Session()


@router.message(F.text == "Адрес")
async def show_address(message: Message):
    await message.answer(
        "Улица: Столетова 2 \nПодъезд: 7 \nЭтаж: 9 \nКвартира: 241 \nЛифт в доме находится на втором этаже! \nhttps://clck.ru/39mGJy",
        reply_markup=back_to_main_menu(),
    )
