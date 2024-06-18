from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def appointment_cancel_keyboard(appointments):
    buttons = []
    for appointment in appointments:
        button_text = f"{appointment.appointment_date.strftime('%d-%m-%Y %H:%M')} - {appointment.user.name}"
        button = InlineKeyboardButton(text=button_text, callback_data=f"cancel_{appointment.id}")
        buttons.append([button])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb