from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from sqlalchemy.orm import Session

from data.utils.appointments_utils import get_appointment
from data.utils.users_utils import get_user
from data.models.user import Role
from extensions.datetime_extensions import ru_datetime

from enums.command import Command
from extensions.command_parser import ComplexCommand

from config.settings import PRICE_URL


def show_main_menu(
    session: Session,
    user_id: int,
    message_id: int,
    context: CallbackContext,
):
    is_exist = get_appointment(session, user_id)
    keyboard: list[list[InlineKeyboardButton]] = []
    if not is_exist:
        keyboard.append(
            [
                InlineKeyboardButton(text="Прайс", callback_data=Command.PRICE.name),
                InlineKeyboardButton(
                    text="Записаться",
                    callback_data=Command.CURRENT_MONTH.name,
                ),
            ]
        )
    else:
        keyboard.append(
            [
                InlineKeyboardButton(text="Прайс", callback_data=Command.PRICE.name),
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Отменить запись",
                    callback_data=Command.CANCEL_APPOINTMENT_LIST.name,
                ),
                InlineKeyboardButton(
                    text="Перенести запись",
                    callback_data=Command.RESCHEDULE_APPOINTMENT_LIST.name,
                ),
            ],
        )

    user = get_user(session=session, chat_id=user_id)
    if user and user.role in (Role.MASTER or user.role, Role.ADMINISTRATOR):
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Ближайшие записи",
                    callback_data=Command.COMING_APPOINTMENTS.name,
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=user_id, text="Выберите опцию:", reply_markup=reply_markup
    )
    if message_id:
        context.bot.delete_message(chat_id=user_id, message_id=message_id)


def show_master_menu(
    master_id: int, message_id: int, command: ComplexCommand, context: CallbackContext
):
    keyboard = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=Command.COMING_APPOINTMENTS.name,
            ),
        ],
        [
            InlineKeyboardButton(
                text="Отправить напоминание",
                callback_data=f"{Command.SEND_NOTIFICATION.name}__{Command.UNDEFINED.name}__{ru_datetime(command.date_time)}__{command.entity_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Перенести запись",
                callback_data=f"{Command.CURRENT_MONTH.name}__{Command.MASTER_RESCHEDULE.name}__{ru_datetime(command.date_time)}__{command.entity_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Отменить запись",
                callback_data=f"{Command.MASTER_CANCEL.name}__{Command.UNDEFINED.name}__{ru_datetime(command.date_time)}__{command.entity_id}",
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.edit_message_reply_markup(
        chat_id=master_id, message_id=message_id, reply_markup=reply_markup
    )


def get_price(
    session: Session, user_id: int, message_id: int, context: CallbackContext
):
    context.bot.send_photo(
        chat_id=user_id,
        photo=PRICE_URL,
    )
    show_main_menu(session, user_id, message_id, context)
