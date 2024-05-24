from aiogram import Router, F
from aiogram.types import Message
from keyboards.user.main_menu import all_steps_button
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from secret import  db_connect
router = Router()

Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


@router.message(F.text == "Вернуться в главное меню")
async def show_main_menu(message: Message):
    await message.answer("Выберите действие:", reply_markup=all_steps_button())

@router.message(F.text == "Выйти из админ панели")
async def show_main_menu(message: Message):
    await message.answer("Выберите действие:", reply_markup=all_steps_button())
