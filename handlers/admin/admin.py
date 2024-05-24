from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command
from keyboards.admin.main_menu import admin_keyboard
from keyboards.admin.admin_list import admin_list_keyboard
from keyboards.admin.create.choose_time import time_keyboard
from keyboards.admin.delete.choose_type import delete_type
from states import CreateAppointmentStep, DeleteAllDayStep, DeleteTimeStep, AddAdmin, DeleteAdmin
from all_calendars import telegramcalendar
from all_calendars import current_calendar
from keyboards.admin.delete.choose_time import time_delete_keyboard
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from datetime import datetime
from aiogram import types
from models import AvailableTime, Appointment, User
from secret import  db_connect
from babel.dates import format_datetime
import json
import os
router = Router()

Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

admins_file = 'admin_list.json'

def load_admins():
    if os.path.exists(admins_file):
        with open(admins_file, 'r') as file:
            return json.load(file)
    else:
        # Если файл не существует, создаем пустой файл и возвращаем пустой словарь
        with open(admins_file, 'w') as file:
            json.dump({}, file)
        return {}

admins = load_admins()

def is_admin(user_id):
    for name, telegram_id in admins.items():
        if user_id == telegram_id:
            return True
    return False

def save_admins(admins):
    with open(admins_file, 'w') as file:
        json.dump(admins, file)

@router.message(Command("startadmin"))
async def start_admin(message: Message):
    if not admins:
        admins['initial_admin'] = message.from_user.id
        save_admins(admins)
        await message.answer("Вы были назначены администратором. Теперь вы можете добавлять других администраторов.")
    else:
        await message.answer("Администратор уже существует.")

@router.message(Command("admin"))
async def admin_menu(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("Добро пожаловать в admin панель, для изменения списка администраторов введите 'Admin list'", reply_markup=admin_keyboard())


@router.message(F.text == "Добавить запись")
async def add_appointment(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
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
            year=year,
            month=month,
            day=day,
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
            selected_times = data.get("selected_times", set())
            year = data.get("year")
            month = data.get("month")
            day = data.get("day")
            date = datetime(year, month, day).date()

            available_time = session.query(AvailableTime).filter_by(date=date).first()
            if available_time:
                existing_times = set([time.strftime('%H:%M') for time in available_time.times])
                all_times = sorted(existing_times.union(selected_times))
                available_time.times = [datetime.strptime(t, '%H:%M').time() for t in all_times]
            else:
                available_time = AvailableTime(date=date, times=sorted([datetime.strptime(t, '%H:%M').time() for t in selected_times]))
                session.add(available_time)
                
            session.commit()
            formatted_times = ", ".join(sorted(selected_times))
            await callback.message.answer(
                f"Вы успешно создали запись: {date} : {formatted_times}"
            )
            await state.clear()
            await callback.message.delete()
        else:
            selected_time = callback.data
            data = await state.get_data()
            times = data.get("selected_times", set())
            if selected_time not in times:
                times.add(selected_time)
                await state.update_data(selected_times=times)
            else:
                await callback.message.answer(
                    f"Время {selected_time} уже выбрано. Выберите другое время."
                )
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()


@router.message(F.text == "Свободные окошки")
async def show_all_appointment(message: Message, state: FSMContext):
    session = Session()
    try:
        if is_admin(message.from_user.id):
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
async def delete_appointment(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
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

@router.message(F.text == "Активные записи")
async def show_active_appointment(message: Message, state: FSMContext):
    session = Session()
    try:
        if is_admin(message.from_user.id):
            appointments = (
                session.query(Appointment)
                .join(User)
                .filter(Appointment.appointment_date > datetime.now())
                .order_by(Appointment.appointment_date)
                .all()
            )
            formatted_appointments = "\n".join(
                [
                    f"{format_datetime(a.appointment_date, format='d MMMM yyyy', locale='ru')} {a.appointment_date.strftime('%H:%M')} {a.user.name} {a.user.contact} {a.user.instagram}"
                    for a in appointments
                ]
            )
            await message.answer(f"Все записи:\n{formatted_appointments}")
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()

@router.message(F.text == "Прошлые записи")
async def show_past_appointment(message: Message, state: FSMContext):
    session = Session()
    try:
        if is_admin(message.from_user.id):
            appointments = (
                session.query(Appointment)
                .join(User)
                .filter(Appointment.appointment_date < datetime.now())  
                .order_by(Appointment.appointment_date.desc())  
                .all()
            )
            formatted_appointments = "\n".join(
                [
                    f"{format_datetime(a.appointment_date, format='d MMMM yyyy', locale='ru')} {a.appointment_date.strftime('%H:%M')} {a.user.name} {a.user.contact} {a.user.instagram}"
                    for a in appointments
                ]
            )
            await message.answer(f"Прошлые записи:\n{formatted_appointments}")
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()

@router.message(F.text == "Список пользователей")
async def show_user_list(message: Message, state: FSMContext):
    session = Session()
    try:
        if is_admin(message.from_user.id):
            users = (
                session.query(User)
                .outerjoin(Appointment)
                .with_entities(
                    User.name,
                    User.contact,
                    User.instagram,
                    User.visit_count,
                    User.telegram_id,
                )
                .order_by(User.name)
                .all()
            )
            formatted_users = "\n".join(
                [
                    f"{user.name} {user.contact} {user.instagram} посещений: {user.visit_count} telegramID: {user.telegram_id}"
                    for user in users
                ]
            )
            await message.answer(f"Список пользователей:\n{formatted_users}")
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()


@router.message(F.text == "Admin list")
async def admin_list(message: Message):
    if is_admin(message.from_user.id):
        admin_list_str = "\n".join([f"{name}: {telegram_id}" for name, telegram_id in admins.items()])
        response_message = f"Список администраторов:\n{admin_list_str}\n\n"
        await message.answer(f"Список администраторов:\n{admin_list_str}\n\n", reply_markup=admin_list_keyboard())

@router.message(F.text == "Добавить администратора")
async def add_admin(message: Message,state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("Введите имя нового администратора:")
        await state.set_state(AddAdmin.enter_name)

@router.message(F.text == "Удалить администратора")
async def delete_admin(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("Введите имя администратора, которого нужно удалить:")
        await state.set_state(DeleteAdmin.enter_name)

@router.message(AddAdmin.enter_name)
async def process_enter_name(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        new_admin_name = message.text
        await state.update_data(new_admin_name=new_admin_name)
        await message.answer("Введите Telegram ID нового администратора:")
        await state.set_state(AddAdmin.enter_id)

@router.message(AddAdmin.enter_id)
async def process_enter_id(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        new_admin_id = int(message.text)
        data = await state.get_data()
        new_admin_name = data.get("new_admin_name")
        admins[new_admin_name] = new_admin_id
        save_admins(admins)
        await message.answer(f"Администратор {new_admin_name} успешно добавлен.",reply_markup=admin_keyboard())
        await state.clear()

@router.message(DeleteAdmin.enter_name)
async def process_delete_name(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        admin_name_to_delete = message.text
        if admin_name_to_delete in admins:
            del admins[admin_name_to_delete]
            save_admins(admins)
            await message.answer(f"Администратор {admin_name_to_delete} успешно удален.", reply_markup=admin_keyboard())
        else:
            await message.answer(f"Администратор с именем {admin_name_to_delete} не найден.", reply_markup=admin_keyboard())
        await state.clear()

@router.message(F.text == "Назад")
async def show_admin_menu(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("Выберите действие:", reply_markup=admin_keyboard())