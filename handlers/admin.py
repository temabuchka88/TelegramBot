from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.admin.admin import admin_keyboard
from keyboards.admin.time_appointment import time_keyboard
from keyboards.admin.choose__type_delete import delete_type
from states import CreateAppointmentStep, DeleteAllDayStep, DeleteTimeStep
from . import telegramcalendar
from . import current_calendar
from keyboards.admin.time_delete import time_delete_keyboard
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from datetime import datetime
from aiogram import types
from models import AvailableTime
from secret import  db_connect

router = Router()

Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


@router.message(F.text == "Admin")
async def admin_menu(message: Message):
    if message.from_user.id == 558165433 or message.from_user.id == 307250457:
        await message.answer("Admin панель", reply_markup=admin_keyboard())


@router.message(F.text == "Добавить запись")
async def add_appointment(message: Message, state: FSMContext):
    if message.from_user.id == 558165433 or message.from_user.id == 307250457:
        await message.reply(
            "Выберите дату: ", reply_markup=telegramcalendar.create_calendar()
        )
        await state.set_state(CreateAppointmentStep.choose_date)


@router.callback_query(CreateAppointmentStep.choose_date)
async def process_calendar_button(callback: types.CallbackQuery, state: FSMContext):
    data = telegramcalendar.separate_callback_data(callback.data)
    if data[0] == "DAY":
        year, month, day = map(int, data[1:])
        await state.update_data(
            year=datetime(year, 1, 1).year,
            month=datetime(year, month, 1).month,
            day=datetime(year, month, day).day,
        )
        await callback.message.edit_text(
            "Выберите время:", reply_markup=time_keyboard()
        )
        await state.set_state(CreateAppointmentStep.choose_time)


@router.callback_query(CreateAppointmentStep.choose_time)
async def process_time_selection(callback: types.CallbackQuery, state: FSMContext):
    session = Session()
    try:
        if callback.data == "accept":
            data = await state.get_data()
            times = data.get("selected_times", [])
            year = data.get("year")
            month = data.get("month")
            day = data.get("day")
            date = datetime(year, month, day).date()
            available_time = AvailableTime(date=date, times=times)
            session.add(available_time)
            session.commit()
            formatted_times = ", ".join(sorted(times))
            await callback.message.answer(
                f"Вы успешно создали запись: {date} : {formatted_times}"
            )
            await state.clear()
            await callback.message.delete()
        else:
            selected_time = callback.data
            data = await state.get_data()
            times = data.get("selected_times", [])
            times.append(selected_time)
            await state.update_data(selected_times=times)
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()


@router.message(F.text == "Все записи")
async def show_all_appointment(message: Message, state: FSMContext):
    session = Session()
    try:
        if message.from_user.id == 558165433 or message.from_user.id == 307250457:
            appointments = (
                session.query(AvailableTime)
                .order_by(
                    AvailableTime.date,
                )
                .all()
            )
            formatted_appointments = "\n".join(
                [
                    f"Дата: {a.date}, время: {', '.join([time.strftime('%H:%M') for time in sorted(a.times)])}"
                    for a in appointments
                ]
            )
            await message.answer(f"Все записи:\n{formatted_appointments}")
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()


@router.message(F.text == "Удалить запись")
async def show_all_appointment(message: Message, state: FSMContext):
    if message.from_user.id == 558165433 or message.from_user.id == 307250457:
        await message.reply(
            f"Вы хотите удалить весь день с записи или какую-то конкретную запись?",
            reply_markup=delete_type(),
        )
        await state.set_state(DeleteAllDayStep.choose_date)

@router.callback_query(F.data == "delete_full_day")
async def delete_select_day(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выберите дату для удаления: ",
        reply_markup=current_calendar.create_current_calendar(),
    )
    await state.set_state(DeleteAllDayStep.delete_day)


@router.callback_query(DeleteAllDayStep.delete_day)
async def delete_all_day(callback: types.CallbackQuery, state: FSMContext):
    session = Session()
    try:
        data = current_calendar.separate_callback_data(callback.data)
        if data[0] == "DAY":
            action, year, month, day = callback.data.split(";")
            year, month, day = map(int, (year, month, day))
            year = datetime(year, 1, 1).year
            month = datetime(year, month, 1).month
            day = datetime(year, month, day).day
            date = datetime(year, month, day).date()
            appointment = (
                session.query(AvailableTime).filter(AvailableTime.date == date).first()
            )
            session.delete(appointment)
            session.commit()
            await callback.message.edit_text(
                f"Вы успешно удалили запись: {date}", reply_markup=None
            )
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()


@router.callback_query(F.data == "delete_time")
async def delete_select_day(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выберите дату: ",
        reply_markup=current_calendar.create_current_calendar(),
    )
    await state.set_state(DeleteTimeStep.choose_date)


@router.callback_query(DeleteTimeStep.choose_date)
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
                    "Выберите время для удаления: ",
                    reply_markup=time_delete_keyboard(formatted_times),
                )
                await state.set_state(DeleteTimeStep.delete_time)
            else:
                await callback.message.edit_text("На выбранную дату записей нет.")
        else:
            await callback.message.edit_text("Ошибка выбора даты.")
            await state.set_state(DeleteTimeStep.choose_date)
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()


@router.callback_query(DeleteTimeStep.delete_time)
async def delete_selected_time(callback: types.CallbackQuery, state: FSMContext):
    session = Session()
    try:
        if callback.data == "accept":
            data = await state.get_data()
            selected_times = data.get("selected_times", [])
            if selected_times:
                appointment_date = datetime(data["year"], data["month"], data["day"]).date()
                appointment = (
                    session.query(AvailableTime)
                    .filter(AvailableTime.date == appointment_date)
                    .first()
                )
                if appointment:
                    selected_times_datetime = [datetime.strptime(time, "%H:%M").time() for time in selected_times]
                    remaining_times = [time for time in appointment.times if time not in selected_times_datetime]
                    if remaining_times:
                        appointment.times = remaining_times
                        session.commit()
                        formatted_remaining_times = ", ".join(sorted(time.strftime("%H:%M") for time in remaining_times))
                        await callback.message.edit_text(
                            f"Успешно удалены времена: {', '.join(selected_times)}\nОставшиеся времена: {formatted_remaining_times}"
                        )
                    else:
                        session.delete(appointment)
                        session.commit()
                        await callback.message.edit_text(
                            f"Успешно удалены времена: {', '.join(selected_times)}\nВсе временные слоты были удалены. Запись удалена."
                        )
                else:
                    await callback.message.edit_text("Ошибка при удалении времен.")
            else:
                await callback.message.edit_text("Выбранные времена не найдены.")
        else:
            selected_time = callback.data
            data = await state.get_data()
            times = data.get("selected_times", [])
            times.append(selected_time)
            await state.update_data(selected_times=times)
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()


