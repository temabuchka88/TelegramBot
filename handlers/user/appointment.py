from aiogram import Router, F, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from datetime import datetime, timedelta
import  time
from models import User, AvailableTime, Appointment
from handlers.admin import current_calendar
from states import AppointmentStep
from keyboards.user.appointment.choose_time import appointment_time_keyboard
from keyboards.user.main_menu import all_steps_button
from keyboards.user.appointment.type_procedure import procedure_keyboard
from babel.dates import format_datetime
from ..admin.admin import load_admins
from sqlalchemy.orm import sessionmaker
from secret import  db_connect
from sqlalchemy import create_engine

connection_string = db_connect
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

router = Router()


async def notify_admins(bot, user_name, user_instagram, user_contact, appointment_time, procedure):
    appointment_date_str = format_datetime(appointment_time, format="d MMMM", locale='ru')
    admins = load_admins()
    appointment_time_str = appointment_time.strftime('%H:%M')
    for admin_id in admins.values():
        await bot.send_message(
            chat_id=admin_id,
            text=(
                f"Пользователь {user_name} записался на {appointment_date_str} в {appointment_time_str} "
                f"на процедуру {procedure.lower()}.\n"
                f"Instagram: {user_instagram}\n"
                f"Номер телефона: {user_contact}."
            )
        )


@router.message(F.text == "Записаться")
async def start_command(message: Message, state: FSMContext):
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        active_appointment = session.query(Appointment).filter_by(user_id=user.id).filter(Appointment.appointment_date > datetime.now()).first()
        if active_appointment:
            await message.reply("Вы уже записаны на другое время.",reply_markup=all_steps_button())
            return
        else:
            await message.reply(
                "Выберите тип процедуры: ", reply_markup=procedure_keyboard()
            )
            await state.set_state(AppointmentStep.choose_type_of_procedure)
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()



@router.callback_query(AppointmentStep.choose_type_of_procedure)
async def choose_type_of_procedure(callback: types.CallbackQuery, state: FSMContext):
    try:
        procedure = callback.data
        await state.update_data(procedure=procedure)
        await callback.message.edit_text(
            "Выберите дату: ", reply_markup=current_calendar.create_current_calendar()
        )
        await state.set_state(AppointmentStep.choose_date)
    except Exception as e:
        print('Произошла ошибка:', e)


@router.callback_query(AppointmentStep.choose_date)
async def appointment_select_day(callback: types.CallbackQuery, state: FSMContext):
    session = Session()
    try:
        data = current_calendar.separate_callback_data(callback.data)
        year, month, day = map(int, data[1:])
        curr = datetime(int(year), int(month), 1)
        if data[0] == "DAY":
            year, month, day = map(int, data[1:])
            date = datetime(year, month, day).date()
            appointment = session.query(AvailableTime).filter(AvailableTime.date == date).first()
            if appointment:
                times = appointment.times
                formatted_times = [time.strftime("%H:%M") for time in times]
                await state.update_data(year=year, month=month, day=day, times=formatted_times)
                await callback.message.edit_text(
                    "Выберите время: ",
                    reply_markup=appointment_time_keyboard(formatted_times),
                )
                await state.set_state(AppointmentStep.confirm_booking)
            else:
                await callback.message.edit_text("На выбранную дату записей нет.")
        elif data[0] == "PREV-MONTH":
            pre = curr - timedelta(days=1)
            await callback.message.edit_text(
                "Выберите дату: ",
                reply_markup=current_calendar.create_current_calendar(int(pre.year), int(pre.month))
            )
        elif data[0] == "NEXT-MONTH":
            ne = curr + timedelta(days=31)
            await callback.message.edit_text(
                "Выберите дату: ",
                reply_markup=current_calendar.create_current_calendar(int(ne.year), int(ne.month))
            )
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()

@router.callback_query(AppointmentStep.confirm_booking)
async def appointment_selected_time(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    session = Session()
    try:
        if callback.data == 'back_to_choose_date':
            data = await state.get_data()
            await callback.message.edit_text(
                "Выберите дату: ",
                reply_markup=current_calendar.create_current_calendar(data["year"], data["month"])
            )
            await state.set_state(AppointmentStep.choose_date)
            return

        data = await state.get_data()
        time_obj = time.strptime(callback.data, '%H:%M')
        appointment_date = datetime(data["year"], data["month"], data["day"], time_obj.tm_hour, time_obj.tm_min)
        user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()
        procedure = data.get("procedure")
        appointment = Appointment(appointment_date=appointment_date, user_id=user.id, procedure=procedure)
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
        await callback.message.edit_text(f'Вы записаны на {appointment_date_str} в {appointment_time_str} на процедуру "{procedure}".\nПо любым вопросам можно написать мне лично: @juliaglin')
        await notify_admins(bot, user.name, user.instagram, user.contact, appointment_date, procedure)
        await state.clear()
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()