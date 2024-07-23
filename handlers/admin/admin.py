from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command
from keyboards.admin.main_menu import admin_keyboard
from keyboards.admin.admin_list import admin_list_keyboard
from keyboards.admin.create.choose_time import time_keyboard
from keyboards.admin.delete.choose_type import delete_type
from states import CreateAppointmentStep, DeleteAllDayStep, DeleteTimeStep, AddAdmin, DeleteAdmin
from handlers.admin import telegramcalendar
from handlers.admin import current_calendar
from keyboards.admin.cancel_appointment import appointment_cancel_keyboard
from keyboards.admin.delete.choose_time import time_delete_keyboard
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from aiogram import types
from models import AvailableTime, Appointment, User
from babel.dates import format_datetime
import json
import os
from sqlalchemy.orm import sessionmaker
from secret import db_connect
from babel.dates import format_date
import collections

connection_string = db_connect
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

router = Router()

admins_file = 'admin_list.json'

def load_admins():
    if os.path.exists(admins_file):
        with open(admins_file, 'r') as file:
            return json.load(file)
    else:
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
        await message.answer("Добро пожаловать в admin панель, для изменения списка администраторов введите '/adminlist'", reply_markup=admin_keyboard())


@router.message(F.text == "Добавить запись")
async def add_appointment(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.reply(
            "Выберите дату: ", reply_markup=telegramcalendar.create_calendar()
        )
        await state.set_state(CreateAppointmentStep.choose_date)


@router.message(F.text == "Добавить запись")
async def add_appointment(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.reply(
            "Выберите дату: ", reply_markup=telegramcalendar.create_calendar()
        )
        await state.set_state(CreateAppointmentStep.choose_date)

@router.callback_query(CreateAppointmentStep.choose_date)
async def process_calendar_button(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = telegramcalendar.separate_callback_data(callback.data)
        action = data[0]

        if action == "accept":
            state_data = await state.get_data()
            selected_days = state_data.get("selected_days", set())
            if not selected_days:
                await callback.message.answer("Вы не выбрали ни одной даты.")
                return

            await callback.message.edit_text("Выберите время:", reply_markup=time_keyboard())
            await state.set_state(CreateAppointmentStep.choose_time)

        else:
            if len(data) != 4:
                raise ValueError("Invalid callback data format")

            year, month, day = int(data[1]), int(data[2]), int(data[3])
            curr = datetime(year, month, 1)

            if action == "PREV-MONTH":
                pre = curr - timedelta(days=1)
                await callback.message.edit_text("Выберите дату(ы):", reply_markup=telegramcalendar.create_calendar(pre.year, pre.month))

            elif action == "NEXT-MONTH":
                ne = curr + timedelta(days=31)
                await callback.message.edit_text("Выберите дату(ы):", reply_markup=telegramcalendar.create_calendar(ne.year, ne.month))

            elif action == "DAY":
                selected_date = datetime(year, month, day).strftime("%Y-%m-%d")
                state_data = await state.get_data()
                selected_days = state_data.get("selected_days", set())

                if selected_date in selected_days:
                    selected_days.remove(selected_date)
                else:
                    selected_days.add(selected_date)

                await state.update_data(selected_days=selected_days)
                
            else:
                await callback.message.answer("Неправильный выбор.")

    except ValueError as e:
        print(f"Error processing calendar button: {e}")
        await callback.message.answer("Произошла ошибка при обработке вашего выбора. Пожалуйста, попробуйте снова.")

@router.callback_query(CreateAppointmentStep.choose_time)
async def process_time_selection(callback: types.CallbackQuery, state: FSMContext):
    session = Session()
    try:
        if callback.data == "accept":
            data = await state.get_data()
            selected_times = data.get("selected_times", set())
            selected_days = data.get("selected_days", set())

            for date_str in selected_days:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()

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
            formatted_dates = ", ".join(sorted(selected_days))
            await callback.message.answer(
                f"Вы успешно создали записи: {formatted_dates} : {formatted_times}"
            )
            await state.clear()
            await callback.message.delete()
        elif callback.data == "custom_time":
            await callback.message.answer("Введите время в формате HH:MM (например, 13:35):")
            await state.set_state(CreateAppointmentStep.enter_custom_time)
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

@router.message(CreateAppointmentStep.enter_custom_time)
async def process_custom_time_input(message: Message, state: FSMContext):
    session = Session()
    try:
        custom_time = message.text
        try:
            datetime.strptime(custom_time, '%H:%M')
        except ValueError:
            await message.answer("Неверный формат времени. Пожалуйста, введите время в формате HH:MM (например, 13:35).")
            return
        
        data = await state.get_data()
        selected_times = data.get("selected_times", set())
        selected_times.add(custom_time)
        await state.update_data(selected_times=selected_times)
        await message.answer(f"Время {custom_time} добавлено. Выберите другие времена или подтвердите выбор.", reply_markup=time_keyboard())
        await state.set_state(CreateAppointmentStep.choose_time)
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

            if not appointments:
                await message.answer("Нет доступных свободных окошек.")
                return

            formatted_appointments = "\n\n".join(
                [
                    f"Дата: {format_date(a.date, format='d MMMM, EEEE', locale='ru')}\nВремя: {', '.join([time.strftime('%H:%M') for time in sorted(a.times)])}"
                    for a in appointments
                ]
            )
            await message.answer(f"Все записи:\n\n{formatted_appointments}")
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
        year, month, day = map(int, data[1:])
        curr = datetime(int(year), int(month), 1)
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
        elif data[0] == "PREV-MONTH":
            pre = curr - timedelta(days=1)
            await callback.message.edit_text(
                "Выберите время:", reply_markup=(current_calendar.create_current_calendar(int(pre.year),int(pre.month))
            ))
        elif data[0] == "NEXT-MONTH":
            ne = curr + timedelta(days=31)
            await callback.message.edit_text(
                "Выберите время:", reply_markup=(current_calendar.create_current_calendar(int(ne.year),int(ne.month))
            ))
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
        year, month, day = map(int, data[1:])
        curr = datetime(int(year), int(month), 1)
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
        elif data[0] == "PREV-MONTH":
            pre = curr - timedelta(days=1)
            await callback.message.edit_text(
                "Выберите время:", reply_markup=(current_calendar.create_current_calendar(int(pre.year),int(pre.month))
            ))
        elif data[0] == "NEXT-MONTH":
            ne = curr + timedelta(days=31)
            await callback.message.edit_text(
                "Выберите время:", reply_markup=(current_calendar.create_current_calendar(int(ne.year),int(ne.month))
            ))
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
            
            if not appointments:
                await message.answer("Нет активных записей.")
                return

            formatted_appointments = "\n\n".join(
                [
                    f"Дата: {format_datetime(a.appointment_date, format='d MMMM, EEEE', locale='ru')}\n"
                    f"Время: {a.appointment_date.strftime('%H:%M')}\n"
                    f"Имя: {a.user.name}\n"
                    f"Контакт: {a.user.contact}\n"
                    f"Instagram: {a.user.instagram}"
                    for a in appointments
                ]
            )
            await message.answer(f"Все записи:\n\n{formatted_appointments}")
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()

@router.message(F.text == "Отмена записи")
async def show_cancel_appointments(message: Message, state: FSMContext):
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
            
            if not appointments:
                await message.answer("Нет активных записей.")
                return

            kb = appointment_cancel_keyboard(appointments)
            await message.answer("Выберите запись для отмены:", reply_markup=kb)
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()

@router.callback_query(F.data.startswith('cancel_'))
async def cancel_appointment_callback(callback_query: types.CallbackQuery, bot: Bot):
    session = Session()
    try:
        appointment_id = int(callback_query.data.split('_')[1])
        appointment = session.query(Appointment).filter_by(id=appointment_id).first()

        if appointment:
            appointment_time = appointment.appointment_date
            current_time = datetime.now()
            user = appointment.user  # Получаем пользователя записи

            if appointment_time > current_time:
                available_time = session.query(AvailableTime).filter_by(date=appointment_time.date()).first()

                if available_time:
                    appointment_time_obj = appointment_time.time()
                    available_times_list = list(available_time.times)

                    if appointment_time_obj not in available_times_list:
                        available_times_list.append(appointment_time_obj)
                        sorted_times = sorted(available_times_list)
                        available_time.times = collections.OrderedDict((t, True) for t in sorted_times)

                        session.commit()
                    else:
                        del available_time.times[appointment_time_obj]
                        session.commit()
                else:
                    appointment_time_obj = appointment_time.time()
                    new_available_time = AvailableTime(date=appointment_time.date(), times=collections.OrderedDict({appointment_time_obj: True}))
                    session.add(new_available_time)
                    session.commit()

            session.delete(appointment)
            session.commit()

            cancellation_info = (
                f"Дата: {format_datetime(appointment_time, format='d MMMM yyyy, EEEE', locale='ru')}\n"
                f"Время: {appointment_time.strftime('%H:%M')}\n"
                f"Имя: {appointment.user.name}\n"
                f"Контакт: {appointment.user.contact}\n"
                f"Instagram: {appointment.user.instagram}"
            )
            await callback_query.message.reply(f"Отменена запись:\n\n{cancellation_info}")

            user = appointment.user
            # Уведомление пользователя
            user_notification = (
                f"Ваша запись на {format_date(appointment_time, format='d MMMM', locale='ru')} "
                f"в {appointment_time.strftime('%H:%M')} отменена администратором."
            )
            await bot.send_message(user.telegram_id, user_notification)
        else:
            await callback_query.message.reply("У вас нет активных записей.", reply_markup=admin_keyboard())
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
            
            if not appointments:
                await message.answer("Нет прошедших записей.")  
                return

            formatted_appointments = "\n\n".join(
                [
                    f"Дата: {format_datetime(a.appointment_date, format='d MMMM yyyy, EEEE', locale='ru')}\n"
                    f"Время: {a.appointment_date.strftime('%H:%M')}\n"
                    f"Имя: {a.user.name}\n"
                    f"Контакт: {a.user.contact}\n"
                    f"Instagram: {a.user.instagram}"
                    for a in appointments
                ]
            )
            await message.answer(f"Прошлые записи:\n\n{formatted_appointments}")
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
                .with_entities(
                    User.name,
                    User.contact,
                    User.instagram,
                    User.telegram_id,
                )
                .order_by(User.name)
                .all()
            )
            
            if not users:
                await message.answer("Список пользователей пуст.")
                return

            formatted_users = "\n\n".join(
                [
                    f"Имя: {user.name}\nКонтакт: {user.contact}\nInstagram: {user.instagram}\nTelegram ID: {user.telegram_id}"
                    for user in users
                ]
            )
            await message.answer(f"Список пользователей:\n\n{formatted_users}")
    except Exception as e:
        await message.answer('Произошла ошибка:', e)
    finally:
        session.close()



@router.message(Command("adminlist"))
async def admin_list(message: Message):
    if is_admin(message.from_user.id):
        admin_list_str = "\n".join([f"{name}: {telegram_id}" for name, telegram_id in admins.items()])
        response_message = f"Список администраторов:\n\n{admin_list_str}\n"
        await message.answer(response_message, reply_markup=admin_list_keyboard())


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
