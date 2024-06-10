from aiogram import Router, F, Bot
from aiogram.types import Message
from keyboards.user.back_to_main_menu import back_to_main_menu
from models import User, Appointment, AvailableTime
from datetime import datetime
from ..admin.admin import load_admins
from babel.dates import format_datetime
from sqlalchemy.orm import sessionmaker
from secret import  db_connect
from sqlalchemy import create_engine

connection_string = db_connect
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

router = Router()


async def notify_admins_cancel(bot, user_name, appointment_time):
    admins = load_admins()
    appointment_date_str = format_datetime(appointment_time, format="d MMMM", locale='ru')
    appointment_time_str = appointment_time.strftime('%H:%M')
    for admin_id in admins.values():
        await bot.send_message(
            chat_id=admin_id,
            text=f"Пользователь {user_name} отменил запись на {appointment_date_str} в {appointment_time_str}."
        )


@router.message(F.text == "Отменить запись")
async def cancel_appointment(message: Message, bot: Bot):
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        active_appointment = session.query(Appointment).filter_by(user_id=user.id).first()
        if active_appointment:
            appointment_time = active_appointment.appointment_date
            current_time = datetime.now()
            if appointment_time > current_time:
                # Проверяем, есть ли уже объект AvailableTime для этой даты
                available_time = session.query(AvailableTime).filter_by(date=appointment_time.date()).first()
                if available_time:
                    # Добавляем время отменяемой записи к объекту AvailableTime
                    print("Тип времени отменяемой записи:", type(appointment_time.time()))
                    print("Типы времен в списке:", [type(t) for t in available_time.times])
                    available_time.times.append(appointment_time.time())
                    print("Время отменяемой записи:", appointment_time.time())
                    print("Времена в списке AvailableTime после добавления:", available_time.times)
                else:
                    # Создаем новый объект AvailableTime и добавляем в него время отменяемой записи
                    available_time = AvailableTime(date=appointment_time.date(), times=[appointment_time.time()])
                    session.merge(available_time)
                    print("Тип времени отменяемой записи:", type(appointment_time.time()))
                    print("Типы времен в списке:", [type(t) for t in available_time.times])
                    print("Время отменяемой записи:", appointment_time.time())
                    print("Времена в списке AvailableTime после добавления:", available_time.times)
                
                # Удаляем запись пользователя
                session.delete(active_appointment)
                session.commit()
                print("Тип времени отменяемой записи:", type(appointment_time.time()))
                print("Типы времен в списке:", [type(t) for t in available_time.times])
                print("Время отменяемой записи:", appointment_time.time())
                print("Времена в списке AvailableTime после добавления:", available_time.times)
                await message.reply("Ваша запись успешно отменена.", reply_markup=back_to_main_menu())
                await notify_admins_cancel(bot, user.name, appointment_time)
            else:
                session.delete(active_appointment)
                session.commit()
                print("Тип времени отменяемой записи:", type(appointment_time.time()))
                print("Типы времен в списке:", [type(t) for t in available_time.times])
                print("Время отменяемой записи:", appointment_time.time())
                await message.reply("Ваша запись успешно отменена.", reply_markup=back_to_main_menu())
                await notify_admins_cancel(bot, user.name, appointment_time)
        else:
            await message.reply("У вас нет активной записи.", reply_markup=back_to_main_menu())
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()
