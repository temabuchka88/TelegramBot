from aiogram.fsm.state import StatesGroup, State

class RegistrationStep(StatesGroup):
    registration_name = State()
    registration_instagram = State()
    registration_contact = State()


class AppointmentStep(StatesGroup):
    choose_type_of_procedure = State()
    choose_date = State()
    choose_time = State()
    confirm_booking = State()

class AddAdmin(StatesGroup):
    enter_name= State()
    enter_id = State()

class DeleteAdmin(StatesGroup):
    enter_name = State()
