from aiogram import Router, F
from aiogram.types import Message
from keyboards.user.main_menu import all_steps_button

router = Router()

@router.message(F.text == "Адрес")
async def show_address(message: Message):
    address_text = (
        "Адрес: Столетова 2\n"
        "Подъезд: 7\n"
        "Этаж: 9\n"
        "Квартира: 241\n"
        "Лифт в доме находится на втором этаже!\n"
        '<a href="https://clck.ru/39mGJy">Посмотреть на карте</a>'
    )
    await message.answer(address_text, reply_markup=all_steps_button(), parse_mode="HTML")


