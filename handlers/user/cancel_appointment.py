from aiogram import Router, F
from aiogram.types import Message
from keyboards.user.back_to_main_menu import back_to_main_menu
from keyboards.user.appointment.cancel_appointment import cancel_appointment
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from models import User, Appointment, AvailableTime
from secret import  db_connect
from datetime import datetime
router = Router()

Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@router.message(F.text == "Отменить запись")
async def cancel_appointment(message: Message):
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        active_appointment = session.query(Appointment).filter_by(user_id=user.id).first()
        if active_appointment:
            appointment_time = active_appointment.appointment_date
            current_time = datetime.now()
            if appointment_time > current_time:
                available_time = session.query(AvailableTime).filter_by(date=appointment_time.date()).first()
                if available_time:
                    available_time.times.append(appointment_time.time())
                else:
                    available_time = AvailableTime(date=appointment_time.date(), times=[appointment_time.time()])
                    session.add(available_time)
                session.delete(active_appointment)
                session.commit()
                await message.reply("Ваша запись успешно отменена.", reply_markup=back_to_main_menu())
            else:
                session.delete(active_appointment)
                session.commit()
                await message.reply("Ваша запись успешно отменена.", reply_markup=back_to_main_menu())
        else:
            await message.reply("У вас нет активной записи.", reply_markup=back_to_main_menu())
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()