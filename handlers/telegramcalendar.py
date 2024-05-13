from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import datetime
import calendar


def create_callback_data(action, year, month, day):
    """Create the callback data associated to each button"""
    return ";".join([action, str(year), str(month), str(day)])


def separate_callback_data(data):
    """Separate the callback data"""
    return data.split(";")


def create_calendar(year=None, month=None):
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = []
    # First row - Month and Year
    row = []
    row.append(
        InlineKeyboardButton(
            text=calendar.month_name[month] + " " + str(year), callback_data=data_ignore
        )
    )
    keyboard.append(row)
    # Second row - Week Days
    row = []
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        row.append(InlineKeyboardButton(text=day, callback_data=data_ignore))
    keyboard.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data=data_ignore))
            else:
                row.append(
                    InlineKeyboardButton(
                        text=str(day),
                        callback_data=create_callback_data("DAY", year, month, day),
                    )
                )
        keyboard.append(row)
    # Last row - Buttons
    row = []
    row.append(
        InlineKeyboardButton(
            text="<", callback_data=create_callback_data("PREV-MONTH", year, month, 1)
        )
    )
    row.append(InlineKeyboardButton(text=" ", callback_data=data_ignore))
    row.append(
        InlineKeyboardButton(
            text=">", callback_data=create_callback_data("NEXT-MONTH", year, month, 1)
        )
    )
    keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def process_calendar_selection(query: CallbackQuery):
    """
    Process the callback_query. This method generates a new calendar if forward or
    backward is pressed. This method should be called inside a CallbackQueryHandler.
    :param telegram.Bot bot: The bot, as provided by the CallbackQueryHandler
    :param telegram.Update update: The update, as provided by the CallbackQueryHandler
    :return: Returns a tuple (Boolean,datetime.datetime), indicating if a date is selected
                and returning the date if so.
    """
    ret_data = (False, None)
    (action, year, month, day) = separate_callback_data(query.data)
    curr = datetime.datetime(int(year), int(month), 1)
    if action == "IGNORE":
        await query.answer()
    elif action == "DAY":
        await query.message.edit_text(
            text=query.message.text + f"\nYou selected {day}/{month}/{year}"
        )
        ret_data = True, datetime.datetime(int(year), int(month), int(day))
    elif action == "PREV-MONTH":
        pre = curr - datetime.timedelta(days=1)
        await query.message.edit_reply_markup(
            reply_markup=create_calendar(int(pre.year), int(pre.month))
        )
    elif action == "NEXT-MONTH":
        ne = curr + datetime.timedelta(days=31)
        await query.message.edit_reply_markup(
            reply_markup=create_calendar(int(ne.year), int(ne.month))
        )
    else:
        await query.answer(text="Something went wrong!")
    return ret_data
