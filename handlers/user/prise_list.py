from aiogram import Router, F
from aiogram.types import Message, FSInputFile 
from keyboards.user.main_menu import all_steps_button
import os

router = Router()

current_dir = os.path.dirname(os.path.abspath(__file__))
prise_path = os.path.join(current_dir, 'prise.jpg')

@router.message(F.text == "Прайс-лист")
async def show_prise_list(message: Message):
    prise = FSInputFile(prise_path)
    await message.answer_photo(prise, reply_markup=all_steps_button())