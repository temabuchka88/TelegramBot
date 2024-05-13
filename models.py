from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.contact_button import contact_button
from keyboards.choose_step import all_steps_button

from states import RegistrationStep

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    create_engine,
    select,
    text,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from sqlalchemy import Column, Integer, Date, ARRAY, Time, DateTime
from sqlalchemy.orm import relationship
from secret import db_connect
Base = declarative_base()
connection_string = db_connect
engine = create_engine(connection_string)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String)
    instagram = Column(String)
    contact = Column(String)
    # active_appointment_id = Column(Integer, ForeignKey('active_appointments.id'))
    telegram_id = Column(Integer)
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
    user = relationship("User", back_populates="appointment", foreign_keys=[user_id])

# class PastAppointment(Base):
#     __tablename__ = "past_appointments"

#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     appointment_date = Column(Date)
#     user = relationship("User", back_populates="past_appointments", foreign_keys=[user_id])

