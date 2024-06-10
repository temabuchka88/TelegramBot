from aiogram import Router, F
from aiogram.types import Message
from keyboards.user.back_to_main_menu import back_to_main_menu

router = Router()

@router.message(F.text == "Адрес")
async def show_address(message: Message):
    address_text = (
        "🏠 **Адрес**: Столетова 2\n"
        "🏢 **Подъезд**: 7\n"
        "🏢 **Этаж**: 9\n"
        "🚪 **Квартира**: 241\n"
        "🔼 Лифт в доме находится на втором этаже!\n"
        "📍 [Посмотреть на карте](https://clck.ru/39mGJy)"
    )
    await message.answer(address_text, reply_markup=back_to_main_menu())

