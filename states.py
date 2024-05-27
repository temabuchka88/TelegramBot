from aiogram.fsm.state import StatesGroup, State

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


class DeleteAllDayStep(StatesGroup):
    choose_date = State()
    delete_day = State()
  
  
class DeleteTimeStep(StatesGroup):
    choose_date = State()
    choose_time = State()
    delete_time = State()

class AddAdmin(StatesGroup):
    enter_name= State()
    enter_id = State()

class DeleteAdmin(StatesGroup):
    enter_name = State()