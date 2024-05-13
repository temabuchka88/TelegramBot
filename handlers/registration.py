from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.contact_button import contact_button
from keyboards.choose_step import all_steps_button

from states import RegistrationStep
from models import User
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


# class RegistrationStep(StatesGroup):
# registration_name = State()
# registration_instagram = State()
# registration_contact = State()


Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)



@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await message.answer("Привет! Давай быстро зарегистрируем тебя. Введи своё имя:")
    await state.set_state(RegistrationStep.registration_name)


@router.message(RegistrationStep.registration_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer("Отлично, теперь отправь свой ник в instagram:")
    await state.set_state(RegistrationStep.registration_instagram)


@router.message(RegistrationStep.registration_instagram)
async def process_instagram(message: Message, state: FSMContext):
    await state.update_data(user_instagram=message.text)
    await message.answer(
        'И теперь для связи нажми кнопку "Поделиться контактом".',
        reply_markup=contact_button(),
    )
    await state.set_state(RegistrationStep.registration_contact)


@router.message(RegistrationStep.registration_contact)
async def process_contact(message: Message, state: FSMContext):
    session = Session()
    try:
        await state.update_data(user_contact=message.contact.phone_number)
        data = await state.get_data()
        user = User(
            name=data.get("user_name"),
            username = message.from_user.username,
            instagram=data.get("user_instagram"),
            contact=data.get("user_contact"),
            telegram_id=message.from_user.id,
        )
        session.add(user)
        session.commit()
        await message.answer(
            "Спасибо! Теперь у тебя есть возможность записаться.",
            reply_markup=all_steps_button(),
        )
        await state.clear()
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()