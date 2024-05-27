from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.user.send_contact import contact_button
from keyboards.user.main_menu import all_steps_button
from states import RegistrationStep
from models import User
from sqlalchemy.orm import sessionmaker
from secret import  db_connect
from sqlalchemy import create_engine

connection_string = db_connect
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

router = Router()

@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        if user:
            await message.answer("Вы уже зарегистрированы и можете записаться.",reply_markup=all_steps_button())
        else:
            await message.answer("Привет! Давай быстро зарегистрируем тебя. Введи своё имя:")
            await state.set_state(RegistrationStep.registration_name)
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()


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