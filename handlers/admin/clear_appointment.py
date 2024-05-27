from datetime import datetime
from aiogram import Router
from models import AvailableTime
from sqlalchemy.orm import sessionmaker
from secret import  db_connect
from sqlalchemy import create_engine

router = Router()

connection_string = db_connect
engine = create_engine(connection_string)
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