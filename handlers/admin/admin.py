from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command
from keyboards.admin.admin_list import admin_list_keyboard
from keyboards.user.main_menu import all_steps_button
from states import AddAdmin, DeleteAdmin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import os
from sqlalchemy.orm import sessionmaker
from secret import db_connect

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
        await message.answer('<a href="http://68.183.79.114:8000">Админ панель</a>', reply_markup=all_steps_button())


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
        await message.answer(f"Администратор {new_admin_name} успешно добавлен.",reply_markup=admin_list_keyboard())
        await state.clear()

@router.message(DeleteAdmin.enter_name)
async def process_delete_name(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        admin_name_to_delete = message.text
        if admin_name_to_delete in admins:
            del admins[admin_name_to_delete]
            save_admins(admins)
            await message.answer(f"Администратор {admin_name_to_delete} успешно удален.", reply_markup=admin_list_keyboard())
        else:
            await message.answer(f"Администратор с именем {admin_name_to_delete} не найден.", reply_markup=admin_list_keyboard())
        await state.clear()

@router.message(F.text == "Назад")
async def show_admin_menu(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("Выберите действие:", reply_markup=all_steps_button())
