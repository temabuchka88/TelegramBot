import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


from handlers.user import registration
from handlers.admin import admin
from handlers.user import address, appointment, choose_step, profile
from secret import telegram_token

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(telegram_token)

    dp.include_router(registration.router)
    dp.include_router(address.router)
    dp.include_router(choose_step.router)
    dp.include_router(appointment.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)


    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
