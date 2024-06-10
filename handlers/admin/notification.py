from datetime import datetime, timedelta
from aiogram import Bot, Router
from models import User,Appointment
from .admin import load_admins
from sqlalchemy.orm import sessionmaker
from secret import  db_connect
from sqlalchemy import create_engine

connection_string = db_connect
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

router = Router()

async def notify_admins_schedule(bot: Bot):
    admins = load_admins()
    try:
        session = Session()
        tomorrow = datetime.now().date() + timedelta(days=1)
        appointments = session.query(Appointment)\
            .join(User)\
            .filter(Appointment.appointment_date >= tomorrow)\
            .filter(Appointment.appointment_date < tomorrow + timedelta(days=1))\
            .all()

        if appointments:
            appointments_info = "\n\n".join([
                (
                    f"Имя: {appointment.user.name}\n"
                    f"Время: {appointment.appointment_date.strftime('%H:%M')}\n"
                    f"Процедура: {appointment.procedure}\n"
                    f"Instagram: {appointment.user.instagram}\n"
                    f"Номер телефона: {appointment.user.contact}"
                )
                for appointment in appointments
            ])
            message = f"На завтра записаны:\n\n{appointments_info}"
            for admin_id in admins.values():
                await bot.send_message(
                    chat_id=admin_id,
                    text=message
                )
        else:
            for admin_id in admins.values():
                await bot.send_message(
                    chat_id=admin_id,
                    text="На завтра записей нет."
                )
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()