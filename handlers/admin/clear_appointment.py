from datetime import datetime
from aiogram import Router
from models import AvailableTime

from bot import engine
from sqlalchemy.orm import sessionmaker

router = Router()
Session = sessionmaker(bind=engine)

def clear_past_appointments():
    session = Session()
    try:
        today = datetime.now().date()
        session.query(AvailableTime).filter(AvailableTime.date < today).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        print('Произошла ошибка:', e)
    finally:
        session.close()