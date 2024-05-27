import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from secret import telegram_token
from handlers.user import registration
from handlers.admin import admin
from handlers.user import address, appointment, choose_step, profile, cancel_appointment
from handlers.user.notifacation_user import schedule_notifications
from handlers.admin.notification import notify_admins_schedule
from handlers.admin import notification
from handlers.user import notifacation_user
from handlers.admin.clear_appointment import clear_past_appointments
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from secret import db_connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

connection_string = db_connect
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

bot = Bot(telegram_token)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    scheduler = AsyncIOScheduler(temezone="Europe/Minsk")
    scheduler.add_job(schedule_notifications, trigger=CronTrigger(hour=12), kwargs={'bot':bot})
    scheduler.add_job(notify_admins_schedule, trigger=CronTrigger(hour=12), kwargs={'bot':bot})
    scheduler.add_job(notify_admins_schedule, trigger=CronTrigger(hour=20), kwargs={'bot':bot})
    scheduler.add_job(clear_past_appointments, trigger=CronTrigger(hour=20, day_of_week='mon'))
    scheduler.start()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(registration.router)
    dp.include_router(address.router)
    dp.include_router(choose_step.router)
    dp.include_router(appointment.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)
    dp.include_router(cancel_appointment.router)
    dp.include_router(notification.router)
    dp.include_router(notifacation_user.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())