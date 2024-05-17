from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from datetime import datetime
from models import User, AvailableTime, Appointment
from datetime import datetime
from datetime import datetime
import time
from aiogram import types
from . import current_calendar
from states import AppointmentStep
from keyboards.admin.appointment_time import appointment_time_keyboard
from secret import  db_connect
from babel.dates import format_datetime
router = Router()
Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@router.message(F.text == "Записаться")
async def start_command(message: Message, state: FSMContext):
    await message.reply(
        "Выберите дату: ", reply_markup=current_calendar.create_current_calendar()
    )
    await state.set_state(AppointmentStep.choose_date)

@router.callback_query(AppointmentStep.choose_date)
async def delete_select_day(callback: types.CallbackQuery, state: FSMContext):
    session = Session()
    try:
        data = current_calendar.separate_callback_data(callback.data)
        if data[0] == "DAY":
            year, month, day = map(int, data[1:])
            date = datetime(year, month, day).date()
            appointment = (
                session.query(AvailableTime).filter(AvailableTime.date == date).first()
            )
            if appointment:
                times = appointment.times
                formatted_times = [time.strftime("%H:%M") for time in times]
                await state.update_data(
                    year=year, month=month, day=day, times=formatted_times
                )
                await callback.message.edit_text(
                    "Выберите время: ",
                    reply_markup=appointment_time_keyboard(formatted_times),
                )
                await state.set_state(AppointmentStep.confirm_booking)
            else:
                await callback.message.edit_text("На выбранную дату записей нет.")
        else:
            await callback.message.edit_text("Ошибка выбора даты.")
            await state.set_state(AppointmentStep.choose_date)
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()

@router.callback_query(AppointmentStep.confirm_booking)
async def delete_selected_time(callback: types.CallbackQuery, state: FSMContext):
    session = Session()
    try:
        data = await state.get_data()
        time_obj = time.strptime(callback.data, '%H:%M')
        appointment_date = datetime(data["year"], data["month"], data["day"], time_obj.tm_hour,time_obj.tm_min)
        user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()
        appointment = Appointment(appointment_date = appointment_date, user_id=user.id)
        session.add(appointment)
        available_time = session.query(AvailableTime).filter(AvailableTime.date == datetime(data["year"], data["month"], data["day"]).date()).first()
        
        if available_time:
            appointment_time_str = appointment_date.time().strftime('%H:%M:%S')
            available_time.times = [time for time in available_time.times if time.strftime('%H:%M:%S') != appointment_time_str]
            
            if not available_time.times:
                session.delete(available_time)
        session.commit()
        appointment_date_str = format_datetime(appointment_date, format="d MMMM", locale='ru')
        appointment_time_str = appointment_date.strftime('%H:%M')
        await callback.message.edit_text(f'Вы записаны на {appointment_date_str} в {appointment_time_str}')
        await state.clear()
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()