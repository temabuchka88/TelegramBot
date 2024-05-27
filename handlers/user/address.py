from aiogram import Router, F
from aiogram.types import Message
from keyboards.user.back_to_main_menu import back_to_main_menu

router = Router()

@router.message(F.text == "Адрес")
async def show_address(message: Message):
    await message.answer(
        "Улица: Столетова 2 \nПодъезд: 7 \nЭтаж: 9 \nКвартира: 241 \nЛифт в доме находится на втором этаже! \nhttps://clck.ru/39mGJy",
        reply_markup=back_to_main_menu(),
    )
