from sqlalchemy import Column, Integer, String, ForeignKey, Date, ARRAY, Time, DateTime, BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from secret import  db_connect
from sqlalchemy import create_engine

connection_string = db_connect
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)


if not database_exists(engine.url):
    create_database(engine.url)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(BIGINT, primary_key=True)
    name = Column(String)
    username = Column(String)
    instagram = Column(String)
    contact = Column(String)
    telegram_id = Column(BIGINT)
    visit_count = Column(Integer, default=0)
    appointment = relationship("Appointment", back_populates="user")


class AvailableTime(Base):
    __tablename__ = "available_times"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    times = Column(ARRAY(Time))

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    appointment_date = Column(DateTime)
    procedure = Column(String)
    user = relationship("User", back_populates="appointment", foreign_keys=[user_id])

Base.metadata.create_all(engine)