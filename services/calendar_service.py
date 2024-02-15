import calendar
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from sqlalchemy.orm import Session

from data.utils.slots_utils import get_available_days, get_free_slots

from extensions.datetime_extensions import (
    ru_time,
    ru_datetime,
    add_months,
    represent_date_only,
    russian_weekdays,
)

from enums.command import Command

current_month = datetime.today()
next_month = add_months(current_month, 1)


def get_current_month(
    session: Session,
    chat_id: int,
    message_id: int,
    context: CallbackContext,
    command: Command,
    user_id: int,
):
    available_days = get_available_days(session, current_month)
    reply_markup = compose_calendar_keyboard_markup(
        current_month, available_days, command, user_id
    )
    context.bot.send_message(
        chat_id=chat_id, text="Выберите дату и время:", reply_markup=reply_markup
    )
    if message_id:
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)


def get_next_month(
    session: Session,
    chat_id: int,
    message_id: int,
    context: CallbackContext,
    command: Command,
    user_id: int,
):
    available_days = get_available_days(session, next_month)
    reply_markup = compose_calendar_keyboard_markup(
        next_month, available_days, command, user_id
    )
    context.bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=reply_markup
    )


def compose_calendar_keyboard_markup(
    calendar_date: datetime,
    free_slot_days: list[datetime],
    command: Command,
    user_id: int,
):
    # Add header row with month and year
    calendar_keyboard: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Назад в главное меню", callback_data=Command.MAINMENU.name
            ),
        ],
        [
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"{Command.CURRENT_MONTH.name}__{command.name if command else Command.UNDEFINED.name}__dt__{user_id}",
            ),
            InlineKeyboardButton(
                text=represent_date_only(calendar_date),
                callback_data=Command.UNDEFINED.name,
            ),
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"{Command.NEXT_MONTH.name}__{command.name if command else Command.UNDEFINED.name}__dt__{user_id}",
            ),
        ],
    ]

    # Add day names row
    calendar_keyboard.append(
        [
            InlineKeyboardButton(text=day_name, callback_data=Command.UNDEFINED.name)
            for day_name in russian_weekdays
        ]
    )

    if not free_slot_days:
        return InlineKeyboardMarkup(calendar_keyboard)

    # Add day buttons for the selected month
    days_in_month = calendar.monthrange(calendar_date.year, calendar_date.month)[1]
    current_day = datetime(calendar_date.year, calendar_date.month, 1)
    days_row: list[InlineKeyboardButton] = []

    for i in range(1, days_in_month + 1):
        formatted_date = ru_datetime(current_day)
        if any(slot.date() == current_day.date() for slot in free_slot_days):
            days_row.append(
                InlineKeyboardButton(
                    text=f"{i}",
                    callback_data=f"{Command.AVAILABLE_TIME.name}__{command.name if command else Command.UNDEFINED.name}__{formatted_date}__{user_id}",
                )
            )
        else:
            days_row.append(
                InlineKeyboardButton(text=" ", callback_data=Command.UNDEFINED.name)
            )

        if current_day.weekday() == 6:  # Sunday == 6
            calendar_keyboard.append(days_row)
            days_row = []
        current_day += timedelta(days=1)

    # Fill gaps between the first day of month and a beginning of a week
    if len(calendar_keyboard[3]) != 7:
        while len(calendar_keyboard[3]) != 7:
            calendar_keyboard[3].insert(
                0, InlineKeyboardButton(text=" ", callback_data=Command.UNDEFINED.name)
            )

    # Add any remaining days to the last row
    if len(days_row) > 0:
        calendar_keyboard.append(days_row)

    # Fill gaps between the last day of month and an end of a week
    if len(calendar_keyboard[-1]) != 7:
        while len(calendar_keyboard[-1]) != 7:
            calendar_keyboard[-1].insert(
                len(calendar_keyboard[-1]),
                InlineKeyboardButton(text=" ", callback_data=Command.UNDEFINED.name),
            )

    for items in calendar_keyboard[3:]:
        if all(item.callback_data == Command.UNDEFINED.name for item in items):
            calendar_keyboard.remove(items)

    return InlineKeyboardMarkup(calendar_keyboard)


def get_time_table(
    session: Session,
    chat_id: int,
    message_id: int,
    slot_day: datetime,
    context: CallbackContext,
    command: Command,
    user_id: int,
):
    if slot_day:
        time_keyboard_markup = compose_time_keyboard(
            slot_day, session, command, user_id
        )
        context.bot.edit_message_reply_markup(
            chat_id=chat_id, message_id=message_id, reply_markup=time_keyboard_markup
        )


def compose_time_keyboard(
    slot_day: datetime,
    session: Session,
    command: Command,
    user_id: int,
) -> InlineKeyboardMarkup:
    time_table: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=f"{Command.CURRENT_MONTH.name if slot_day.month == datetime.now().month else Command.NEXT_MONTH.name}__{command.name if command else Command.UNDEFINED.name}__dt__{user_id}",
            )
        ]
    ]
    free_slots = get_free_slots(session=session, date_time_slot=slot_day.date())
    if not free_slots:
        return InlineKeyboardMarkup(time_table)

    for slot in free_slots:
        time_table.append(
            [
                InlineKeyboardButton(
                    text=ru_time(slot.date_time_slot),
                    callback_data=f"{command.name if command in (Command.RESCHEDULE_APPOINTMENT, Command.MASTER_RESCHEDULE) else Command.NEW_APPOINTMENT.name}__{Command.UNDEFINED.name}__{ru_datetime(slot.date_time_slot)}__{user_id if command == Command.MASTER_RESCHEDULE else slot.master_id}",
                )
            ]
        )

    return InlineKeyboardMarkup(time_table)
