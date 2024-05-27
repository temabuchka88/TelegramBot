from datetime import datetime, timedelta
from aiogram import Bot, Router
from models import User,Appointment
from .admin import load_admins
from bot import engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

admins = load_admins()
router = Router()

async def notify_admins_schedule(bot: Bot):
    try:
        session = Session()
        tomorrow = datetime.now().date() + timedelta(days=1)
        appointments = session.query(Appointment)\
        .join(User)\
        .filter(Appointment.appointment_date >= tomorrow)\
        .filter(Appointment.appointment_date < tomorrow + timedelta(days=1))\
        .all()

        if appointments:
            appointments_info = "\n".join([f"{appointment.user.name} в {appointment.appointment_date.strftime('%H:%M')}" for appointment in appointments])
            message = f"На завтра записаны:\n{appointments_info}"
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