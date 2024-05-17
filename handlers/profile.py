from aiogram import Router, F
from aiogram.types import Message
from keyboards.user.back_to_main_menu import back_to_main_menu
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from models import User
from secret import  db_connect
router = Router()

Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)



@router.message(F.text == "Мой профиль")
async def show_profile(message: Message):
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        await message.answer(
            f"Имя: {user.name}\nInstagram: {user.instagram}\nКонтактный номер: {user.contact}",
            reply_markup=back_to_main_menu(),
        )
    except Exception as e:
        print('Произошла ошибка:', e)
    finally:
        session.close()
