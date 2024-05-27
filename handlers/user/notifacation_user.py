
from aiogram import Bot, Router, types, F
from datetime import datetime, timedelta
from models import User, Appointment, AvailableTime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from babel.dates import format_datetime
from handlers.user.cancel_appointment import notify_admins_cancel
from keyboards.user.back_to_main_menu import back_to_main_menu
from ..admin.admin import load_admins
from bot import engine
from sqlalchemy.orm import sessionmaker

router = Router()
Session = sessionmaker(bind=engine)
admins = load_admins()


async def schedule_notifications(bot: Bot):
    session = Session()
    tomorrow = datetime.now().date() + timedelta(days=1)
    appointments = session.query(Appointment)\
        .join(User)\
        .filter(Appointment.appointment_date >= tomorrow)\
        .filter(Appointment.appointment_date < tomorrow + timedelta(days=1))\
        .all()

    for appointment in appointments:
        user = appointment.user
        appointment_time = appointment.appointment_date.strftime("%H:%M")
        message = f"Добрый день, {user.name}! Напоминаем вам о вашей записи на завтра в {appointment_time}."
        confirm_button = InlineKeyboardButton(
            text="Подтвердить запись", 
            callback_data=f"confirm|{user.id}|{appointment.appointment_date.isoformat()}"
        )
        cancel_button = InlineKeyboardButton(
            text="Отменить", 
            callback_data=f"cancel|{user.id}|{appointment.appointment_date.isoformat()}"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[confirm_button], [cancel_button]])
        await bot.send_message(user.telegram_id, message, reply_markup=kb)

async def notify_accept(bot: Bot, user_name: str, appointment_time: datetime):
    appointment_date_str = format_datetime(appointment_time, format="d MMMM", locale='ru')
    appointment_time_str = appointment_time.strftime('%H:%M')
    for admin_id in admins.values():
        await bot.send_message(
            chat_id=admin_id,
            text=f"Пользователь {user_name} подтвердил запись на {appointment_date_str} в {appointment_time_str}."
        )

@router.callback_query(F.data.startswith ('confirm'))
async def process_confirmation(callback: types.CallbackQuery):
    try:
        _, user_id, appointment_date = callback.data.split('|')
        session = Session()
        user = session.query(User).filter_by(id=user_id).first()
        appointment_date = datetime.fromisoformat(appointment_date)

        await notify_accept(callback.bot, user.name, appointment_date)
        await callback.message.answer("Вы подтвердили запись.")

    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()

@router.callback_query(F.data.startswith ('cancel'))
async def process_cancellation(callback: types.CallbackQuery):
    _, user_id, appointment_date_str = callback.data.split('|')
    session = Session()

    try:
        user = session.query(User).filter_by(id=user_id).first()
        appointment_date = datetime.fromisoformat(appointment_date_str)

        active_appointment = session.query(Appointment).filter_by(user_id=user.id, appointment_date=appointment_date).first()
        
        if active_appointment:
            if appointment_date > datetime.now():
                available_time = session.query(AvailableTime).filter_by(date=appointment_date.date()).first()
                if available_time:
                    available_time.times.append(appointment_date.time())
                else:
                    available_time = AvailableTime(date=appointment_date.date(), times=[appointment_date.time()])
                    session.add(available_time)
                session.delete(active_appointment)
                session.commit()
                await callback.message.reply("Ваша запись успешно отменена.", reply_markup=back_to_main_menu())
                await notify_admins_cancel(callback.bot, user.name, appointment_date)
            else:
                session.delete(active_appointment)
                session.commit()
                await callback.message.reply("Ваша запись успешно отменена.", reply_markup=back_to_main_menu())
                await notify_admins_cancel(callback.bot, user.name, appointment_date)
        else:
            await callback.message.reply("У вас нет активной записи.", reply_markup=back_to_main_menu())

    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()