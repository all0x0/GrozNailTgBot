from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import CallbackContext

from sqlalchemy.orm import Session

from data.utils.users_utils import get_user
from data.utils.slots_utils import add_slot, get_free_slot, delete_slot
from data.utils.appointments_utils import (
    create_appointment,
    get_appointment,
    get_user_appointments,
    update_reject_appointment,
    get_user_appointments_time,
)
from data.models.appointment import Appointment

from services.main_menu_service import show_main_menu

from extensions.command_parser import ComplexCommand
from extensions.datetime_extensions import ru_datetime, represent_datetime

from enums.command import Command

from config.settings import ADDRESS_PHOTO_URL, ADDRESS_URL


def new_appointment(
    session: Session,
    chat_id: int,
    context: CallbackContext,
    command: ComplexCommand,
):
    user_appointments = get_user_appointments_time(session, chat_id)
    if user_appointments:
        context.bot.send_message(
            chat_id=chat_id,
            text=f"У вас уже есть запись на <b><i>{represent_datetime(user_appointments[0])}</i></b>",
            parse_mode=constants.PARSEMODE_HTML,
        )
        return

    slot = get_free_slot(session, command.user_id, command.date_time)
    if slot is None:
        context.bot.send_message(
            chat_id=chat_id,
            text="Упс, кажется кто-то опередил вас и занял это время, попробуйте выбрать другое время.",
        )
        return

    appointment = Appointment(
        master_id=command.user_id,
        procedure_time=command.date_time,
        user_id=chat_id,
        is_cancelled=False,
    )
    create_appointment(session, appointment)
    delete_slot(session, command.user_id, command.date_time)
    user = get_user(session, chat_id)

    # message to master
    markup_keyboard = compose_answer_keyboard(chat_id, command.date_time)
    context.bot.send_message(
        chat_id=command.user_id,
        text=f"К вам хочет записаться {user.name} на <b><i>{represent_datetime(command.date_time)}</i></b>.",
        reply_markup=markup_keyboard,
        parse_mode=constants.PARSEMODE_HTML,
    )

    # message to user
    context.bot.send_message(
        chat_id=chat_id,
        text=f"Ваш запрос на запись на <b><i>{represent_datetime(command.date_time)}</i></b> успешно отправлен мастеру.\r\nОжидайте ответа от бота.",
        parse_mode=constants.PARSEMODE_HTML,
    )


def cancel_appointment(
    session: Session, chat_id: int, procedure_time: datetime, context: CallbackContext
):
    appointment = get_appointment(session, chat_id, procedure_time)
    update_reject_appointment(session, appointment.id)
    add_slot(session, appointment.master_id, appointment.procedure_time)

    # message to user
    context.bot.send_message(
        chat_id=chat_id,
        text=f"Запись на <b><i>{represent_datetime(appointment.procedure_time)}</i></b> отменена.",
        parse_mode=constants.PARSEMODE_HTML,
    )

    # message to master
    user = get_user(session, chat_id)
    context.bot.send_message(
        chat_id=appointment.master_id,
        text=f"{user.name} отменил запись на <b><i>{represent_datetime(appointment.procedure_time)}</i></b>.",
        parse_mode=constants.PARSEMODE_HTML,
    )


def reschedule_appointment(
    session: Session, chat_id: int, context: CallbackContext, command: ComplexCommand
):
    user_appointments = get_user_appointments(session, chat_id)
    if user_appointments:
        for appointment in user_appointments:
            update_reject_appointment(session, appointment.id)
            add_slot(session, appointment.master_id, appointment.procedure_time)

        slot = get_free_slot(session, command.user_id, command.date_time)
        if slot is None:
            context.bot.send_message(
                chat_id=chat_id,
                text="Упс, кажется кто-то опередил вас и занял это время, попробуйте выбрать другое время.",
            )
            return

        appointment = Appointment(
            master_id=command.user_id,
            procedure_time=command.date_time,
            user_id=chat_id,
            is_cancelled=False,
        )
        create_appointment(session, appointment)
        delete_slot(session, command.user_id, command.date_time)

        user = get_user(session, chat_id)
        # message to master
        markup_keyboard = compose_answer_keyboard(chat_id, command.date_time)
        context.bot.send_message(
            chat_id=command.user_id,
            text=f"{user.name} хочет перенести свою запись с <b><i>{represent_datetime(user_appointments[0].procedure_time)}</i></b> на <b><i>{represent_datetime(command.date_time)}</i></b>.",
            reply_markup=markup_keyboard,
            parse_mode=constants.PARSEMODE_HTML,
        )

        # message to user
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Ваш запрос на перенос записи с <b><i>{represent_datetime(user_appointments[0].procedure_time)}</i></b> на <b><i>{represent_datetime(command.date_time)}</i></b> успешно отправлен мастеру.\r\nОжидайте ответа от бота.",
            parse_mode=constants.PARSEMODE_HTML,
        )


def reject_request(
    session: Session,
    chat_id: int,
    message_id: int,
    command: ComplexCommand,
    context: CallbackContext,
):
    user = get_user(session, command.user_id)
    appointment = get_appointment(session, command.user_id, command.date_time)
    if appointment is None:
        # message to master
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Похоже пользователь {user.name} сам отменил запись на <b><i>{represent_datetime(command.date_time)}</i></b>.",
            parse_mode=constants.PARSEMODE_HTML,
        )
        return

    update_reject_appointment(session, appointment.id)
    add_slot(session, appointment.master_id, appointment.procedure_time)

    # message to master
    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Вы отклонили запрос на запись от {user.name} на <b><i>{represent_datetime(appointment.procedure_time)}</i></b>.",
        parse_mode=constants.PARSEMODE_HTML,
    )

    # message to user
    master = get_user(session, chat_id)
    context.bot.send_message(
        chat_id=command.user_id,
        text=f"Мастер отклонил вашу запись на <b><i>{represent_datetime(appointment.procedure_time)}</i></b>.\r\n"
        + f"Попробуйте выбрать другое свободное окно или свяжитесь с мастером просто кликнув по нику -> {master.telegram}.",
        parse_mode=constants.PARSEMODE_HTML,
    )
    show_main_menu(session, command.user_id, None, context)


def accept_request(
    session: Session,
    master_id: int,
    message_id: int,
    command: ComplexCommand,
    context: CallbackContext,
):
    user = get_user(session, command.user_id)
    appointment = get_appointment(session, command.user_id, command.date_time)
    if appointment is None:
        # message to master
        context.bot.edit_message_text(
            chat_id=master_id,
            message_id=message_id,
            text=f"Похоже пользователь {user.name} отменил запись на <b><i>{represent_datetime(command.date_time)}</i></b>.",
            parse_mode=constants.PARSEMODE_HTML,
        )
        return

    # message to user
    context.bot.send_message(
        chat_id=command.user_id,
        text=f"Мастер подтвердил вашу запись на <b><i>{represent_datetime(command.date_time)}</i></b>.\r\n"
        + "За день до процедуры бот пришлет вам напоминание.",
        parse_mode=constants.PARSEMODE_HTML,
    )

    context.bot.send_photo(
        chat_id=command.user_id,
        photo=ADDRESS_PHOTO_URL,
        caption=f"""
Адрес: {ADDRESS_URL}
Вход в подъезд указан красной стрелочкой.
Поднимайтесь на последний этаж, мастер вас встретит.""",
    )

    # message to master
    context.bot.edit_message_text(
        chat_id=master_id,
        message_id=message_id,
        text=f"{user.name} успешно записан на <b><i>{represent_datetime(command.date_time)}</i></b>.",
        parse_mode=constants.PARSEMODE_HTML,
    )


def get_booked_slots(
    session: Session,
    chat_id: int,
    message_id: int,
    context: CallbackContext,
    menu_command: Command,
):
    slots_to_cancel = get_user_appointments_time(session, chat_id)
    reply_keyboard = compose_time_keyboard(slots_to_cancel, menu_command)
    context.bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=reply_keyboard
    )


def compose_time_keyboard(dates: list[datetime], menu_command: Command):
    keyboard = [
        [InlineKeyboardButton(text="Назад", callback_data=Command.MAINMENU.name)]
    ]

    if len(dates) == 0:
        return InlineKeyboardMarkup(keyboard)

    if menu_command == Command.CANCEL_APPOINTMENT:
        for slot in dates:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=represent_datetime(slot),
                        callback_data=f"{menu_command.name}__{menu_command.name}__{ru_datetime(slot)}",
                    )
                ]
            )
    if menu_command == Command.RESCHEDULE_APPOINTMENT:
        for slot in dates:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=represent_datetime(slot),
                        callback_data=f"{Command.CURRENT_MONTH.name}__{menu_command.name}__{ru_datetime(slot)}",
                    )
                ]
            )

    return InlineKeyboardMarkup(keyboard)


def compose_answer_keyboard(chat_id: int, date_time: datetime):
    keyboard = [
        [
            InlineKeyboardButton(
                text="Принять",
                callback_data=f"{Command.ACCEPT_REQUEST.name}__{Command.UNDEFINED.name}__{ru_datetime(date_time)}__{chat_id}",
            ),
            InlineKeyboardButton(
                text="Отклонить",
                callback_data=f"{Command.REJECT_REQUEST.name}__{Command.UNDEFINED.name}__{ru_datetime(date_time)}__{chat_id}",
            ),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)
