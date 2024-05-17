from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.user.contact_button import contact_button


# class AllStep(StatesGroup):
#     registration = State()
#     appointment = State()
#     address = State()
#     profile = State()


class RegistrationStep(StatesGroup):
    registration_name = State()
    registration_instagram = State()
    registration_contact = State()


class AppointmentStep(StatesGroup):
    choose_date = State()
    choose_time = State()
    confirm_booking = State()


class CreateAppointmentStep(StatesGroup):
    choose_date = State()
    choose_time = State()
    create_appointment = State()


# class ProfileStep(StatesGroup):
#     view_profile = State()
#     edit_profile = State()


class DeleteAllDayStep(StatesGroup):
    choose_date = State()
    delete_day = State()


class DeleteTimeStep(StatesGroup):
    choose_date = State()
    choose_time = State()
    delete_time = State()
