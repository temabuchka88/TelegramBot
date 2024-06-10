from aiogram import Router, F
from aiogram.types import Message
from keyboards.user.back_to_main_menu import back_to_main_menu
from keyboards.user.appointment.cancel_appointment import cancel_appointment
from models import User, Appointment
from datetime import datetime
from babel.dates import format_datetime
from sqlalchemy.orm import sessionmaker
from secret import  db_connect
from sqlalchemy import create_engine

connection_string = db_connect
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

router = Router()


@router.message(F.text == "Мой профиль")
async def show_profile(message: Message):
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        active_appointment = session.query(Appointment).filter_by(user_id=user.id).filter(Appointment.appointment_date > datetime.now()).first()
        
        if active_appointment:
            active_appointment_text = format_datetime(active_appointment.appointment_date, format="d MMMM в H:mm", locale='ru')
            profile_text = (
                f"👤 Имя: {user.name}\n"
                f"📅 Активная запись: {active_appointment_text}"
            )
            await message.answer(
                profile_text,
                reply_markup=cancel_appointment()
            )
        else:
            profile_text = (
                f"👤 Имя: {user.name}\n"
                f"📅 Активная запись: Нет активной записи"
            )
            await message.answer(
                profile_text,
                reply_markup=back_to_main_menu()
            )

    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()
