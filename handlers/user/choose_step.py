from aiogram import Router, F
from aiogram.types import Message
from keyboards.user.main_menu import all_steps_button

router = Router()


@router.message(F.text == "Вернуться в главное меню")
async def show_main_menu(message: Message):
    await message.answer("Выберите действие:", reply_markup=all_steps_button())
