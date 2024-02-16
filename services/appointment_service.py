from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import CallbackContext

from sqlalchemy.orm import Session

from data.utils.users_utils import get_user
from data.utils.slots_utils import add_slot, get_free_slot, delete_slot
from data.utils.appointments_utils import (
    create_appointment,
    get_appointment,
    get_user_appointments_time,
    check_appointments_for_master,
    update_appointment,
)
from data.models.appointment import Appointment

from services.main_menu_service import show_main_menu

from extensions.command_parser import ComplexCommand
from extensions.datetime_extensions import ru_datetime, represent_datetime

from enums.command import Command

from config.settings import ADDRESS_PHOTO_URL, ADDRESS_URL


def new_appointment(
    session: Session,
    username: str,
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

    slot = get_free_slot(session, command.entity_id, command.date_time)
    if slot is None:
        context.bot.send_message(
            chat_id=chat_id,
            text="Упс, кажется кто-то опередил вас и занял это время, попробуйте выбрать другое время.",
        )
        return

    appointment = Appointment(
        master_id=command.entity_id,
        procedure_time=command.date_time,
        user_name=username,
        user_id=chat_id,
        is_cancelled=False,
    )
    create_appointment(session, appointment)
    delete_slot(session, command.entity_id, command.date_time)
    user = get_user(session, chat_id)

    # message to master
    markup_keyboard = compose_answer_keyboard(chat_id, command.date_time)
    context.bot.send_message(
        chat_id=command.entity_id,
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
    session: Session,
    chat_id: int,
    context: CallbackContext,
):
    appointment = get_appointment(session, chat_id)
    if appointment:
        update_appointment(
            session, appointment.id, is_cancelled=True, is_provided=False
        )
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
    appointment = get_appointment(session, chat_id)
    if appointment:
        slot = get_free_slot(session, command.entity_id, command.date_time)
        if slot is None:
            context.bot.send_message(
                chat_id=chat_id,
                text="Упс, кажется кто-то опередил вас и занял это время, попробуйте выбрать другое время.",
            )
            return

        add_slot(session, appointment.master_id, appointment.procedure_time)
        old_time = appointment.procedure_time
        update_appointment(session, appointment.id, procedure_time=command.date_time)
        delete_slot(session, command.entity_id, command.date_time)

        # message to master
        markup_keyboard = compose_answer_keyboard(chat_id, command.date_time)
        context.bot.send_message(
            chat_id=command.entity_id,
            text=f"{appointment.user_name} хочет перенести свою запись с <b><i>{represent_datetime(old_time)}</i></b> на <b><i>{represent_datetime(command.date_time)}</i></b>.",
            reply_markup=markup_keyboard,
            parse_mode=constants.PARSEMODE_HTML,
        )

        # message to user
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Ваш запрос на перенос записи с <b><i>{represent_datetime(old_time)}</i></b> на <b><i>{represent_datetime(command.date_time)}</i></b> успешно отправлен мастеру.\r\nОжидайте ответа от бота.",
            parse_mode=constants.PARSEMODE_HTML,
        )


def master_reschedule_appointment(
    session: Session, chat_id: int, context: CallbackContext, command: ComplexCommand
):
    appointment = get_appointment(session, command.entity_id)
    if appointment:
        slot = get_free_slot(session, chat_id, command.date_time)
        if slot is None:
            context.bot.send_message(
                chat_id=chat_id,
                text="Упс, кажется кто-то опередил вас и занял это время, попробуйте выбрать другое время.",
            )
            return

        add_slot(session, appointment.master_id, appointment.procedure_time)
        old_time = appointment.procedure_time
        update_appointment(session, appointment.id, procedure_time=command.date_time)
        delete_slot(session, chat_id, command.date_time)

        # message to master
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Запись пользователя {appointment.user_name} перенесена с <b><i>{represent_datetime(old_time)}</i></b> на <b><i>{represent_datetime(command.date_time)}</i></b>.",
            parse_mode=constants.PARSEMODE_HTML,
        )

        # message to user
        context.bot.send_message(
            chat_id=command.entity_id,
            text=f"Мастер перенес вашу запись с <b><i>{represent_datetime(old_time)}</i></b> на <b><i>{represent_datetime(command.date_time)}</i></b>.\r\nОжидайте ответа от бота.",
            parse_mode=constants.PARSEMODE_HTML,
        )


def reject_request(
    session: Session,
    chat_id: int,
    message_id: int,
    command: ComplexCommand,
    context: CallbackContext,
    is_master: bool,
):
    user = get_user(session, command.entity_id)
    appointment = get_appointment(session, command.entity_id)
    if appointment is None:
        # message to master
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Похоже пользователь {user.name} сам отменил запись на <b><i>{represent_datetime(command.date_time)}</i></b>.",
            parse_mode=constants.PARSEMODE_HTML,
        )
        return

    update_appointment(session, appointment.id, is_cancelled=True, is_provided=False)
    add_slot(session, appointment.master_id, appointment.procedure_time)

    # message to master
    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Вы {'отменили' if is_master else 'отклонили запрос на'} запись от {user.name} на <b><i>{represent_datetime(appointment.procedure_time)}</i></b>.",
        parse_mode=constants.PARSEMODE_HTML,
    )

    # message to user
    master = get_user(session, chat_id)
    context.bot.send_message(
        chat_id=command.entity_id,
        text=f"Мастер {'отменил' if is_master else 'отклонил'} вашу запись на <b><i>{represent_datetime(appointment.procedure_time)}</i></b>.\r\n"
        + f"Попробуйте выбрать другое свободное окно или свяжитесь с мастером просто кликнув по нику -> {master.telegram}.",
        parse_mode=constants.PARSEMODE_HTML,
    )
    show_main_menu(session, command.entity_id, None, context)


def accept_request(
    session: Session,
    master_id: int,
    message_id: int,
    command: ComplexCommand,
    context: CallbackContext,
):
    user = get_user(session, command.entity_id)
    appointment = get_appointment(session, command.entity_id)
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
        chat_id=command.entity_id,
        text=f"Мастер подтвердил вашу запись на <b><i>{represent_datetime(command.date_time)}</i></b>.\r\n"
        + "За день до процедуры бот пришлет вам напоминание.",
        parse_mode=constants.PARSEMODE_HTML,
    )

    context.bot.send_photo(
        chat_id=command.entity_id,
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


def show_coming_appointments(
    session: Session, chat_id: int, message_id: int, context: CallbackContext
):
    keyboard = [
        [InlineKeyboardButton(text="Назад", callback_data=Command.MAINMENU.name)]
    ]
    appointments = check_appointments_for_master(session=session, master_id=chat_id)

    for appointment in appointments:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{appointment.user_name} на {ru_datetime(appointment.procedure_time)}",
                    callback_data=f"{Command.MASTER_MENU.name}__{Command.UNDEFINED.name}__{ru_datetime(appointment.procedure_time)}__{appointment.user_id}",
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=reply_markup
    )


def send_notification(user_id: int, date_time: datetime, context: CallbackContext):
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Подтвердить",
                    callback_data=Command.CONFIRM_REMINDER.name,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Отклонить",
                    callback_data=Command.DECLINE_REMINDER.name,
                )
            ],
        ]
    )

    context.bot.send_message(
        chat_id=user_id,
        text=f"Здравствуйте! Напоминаю что вы записаны на маникюр <b><i>{represent_datetime(date_time)}</i></b>.\r\nПодтвердите пожалуйста запись.",
        reply_markup=reply_markup,
        parse_mode=constants.PARSEMODE_HTML,
    )


def confirm_reminder(
    session: Session,
    user_id: int,
    message_id: int,
    context: CallbackContext,
):
    appointment = get_appointment(session, user_id)
    if appointment:
        update_appointment(session, appointment.id, is_confirmed=True)

        # message to user
        if message_id:
            context.bot.delete_message(chat_id=user_id, message_id=message_id)

        context.bot.send_message(chat_id=user_id, text="Отлично, ждем вас!")

        # message to master
        context.bot.send_message(
            chat_id=appointment.master_id,
            text=f"Запись <b><i>{represent_datetime(appointment.procedure_time)}</i></b> подтверждена.",
            parse_mode=constants.PARSEMODE_HTML,
        )


def decline_reminder(
    session: Session,
    user_id: int,
    message_id: int,
    context: CallbackContext,
):
    appointment = get_appointment(session, user_id)
    if appointment:
        update_appointment(
            session,
            appointment.id,
            is_confirmed=False,
            is_cancelled=True,
            is_provided=False,
        )
        add_slot(session, appointment.master_id, appointment.procedure_time)

        # message to user
        if message_id:
            context.bot.delete_message(chat_id=user_id, message_id=message_id)

        context.bot.send_message(
            chat_id=user_id,
            text="Понимаем вашу занятость, надеемся на встречу в будущем.",
            parse_mode=constants.PARSEMODE_HTML,
        )

        # message to master
        context.bot.send_message(
            chat_id=appointment.master_id,
            text=f"Запись <b><i>{represent_datetime(appointment.procedure_time)}</i></b> отклонена.",
            parse_mode=constants.PARSEMODE_HTML,
        )
