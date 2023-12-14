from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from sqlalchemy.orm import Session

from data.utils.appointments_utils import check_appointments

from enums.command import Command

from config.settings import PRICE_URL


def show_main_menu(
    session: Session,
    user_id: int,
    message_id: int,
    context: CallbackContext,
):
    is_exist = check_appointments(session, user_id)
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

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=user_id, text="Выберите опцию:", reply_markup=reply_markup
    )
    if message_id:
        context.bot.delete_message(chat_id=user_id, message_id=message_id)


def get_price(
    session: Session, user_id: int, message_id: int, context: CallbackContext
):
    context.bot.send_photo(
        chat_id=user_id,
        photo=PRICE_URL,
    )
    show_main_menu(session, user_id, message_id, context)
