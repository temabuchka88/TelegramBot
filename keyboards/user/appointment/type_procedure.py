from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def procedure_keyboard():
    procedures = [
        "Маникюр с покрытием",
        "Маникюр без покрытия",
        "Наращивание",
        "Снятие",
        "Ремонт",
    ]
    buttons = []
    for procedure in procedures:
        button = InlineKeyboardButton(text=procedure, callback_data=procedure)
        buttons.append([button])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb