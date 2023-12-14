from telegram.ext import CallbackContext

from sqlalchemy.orm import Session

from data.utils.users_utils import get_user
from data.utils.slots_utils import add_slots, delete_slots, clear_days
from enums.role import Role
from extensions.datetime_extensions import try_parse_dates


def add_new_slots(
    session: Session,
    user_id: int,
    dates_to_parse: str,
    context: CallbackContext,
):
    existingUser = get_user(session, user_id)
    if existingUser is None or existingUser.role == Role.USER:
        return

    parsed_dates = try_parse_dates(dates_to_parse)
    added_slots = add_slots(session, user_id, parsed_dates)
    if added_slots:
        context.bot.send_message(
            chat_id=user_id,
            text="Успешно добавлены следующие слоты:\n" + "\n".join(added_slots),
        )


def remove_slots(
    session: Session,
    user_id: int,
    dates_to_parse: str,
    context: CallbackContext,
):
    existingUser = get_user(session, user_id)
    if existingUser is None or existingUser.role == Role.USER:
        return

    parsed_dates = try_parse_dates(dates_to_parse)
    deleted_slots = delete_slots(session, user_id, parsed_dates)
    if deleted_slots:
        context.bot.send_message(
            chat_id=user_id,
            text="Успешно удалены следующие слоты:\n" + "\n".join(deleted_slots),
        )


def remove_days(
    session: Session,
    user_id: int,
    dates_to_parse: str,
    context: CallbackContext,
):
    existingUser = get_user(session, user_id)
    if existingUser is None or existingUser.role == Role.USER:
        return

    parsed_dates = try_parse_dates(dates_to_parse, date_format="%Y-%m-%d")
    removed_days = clear_days(session, user_id, parsed_dates)
    if removed_days:
        context.bot.send_message(
            chat_id=user_id,
            text="Успешно очищены следующие дни:\n" + "\n".join(removed_days),
        )


def get_hidden_commands(
    session: Session, user_id: int, context: CallbackContext
):
    existingUser = get_user(session, user_id)
    if existingUser is None or existingUser.role == Role.USER:
        return
    context.bot.send_message(
        chat_id=user_id,
        text="Для добавления новых слотов скопируйте и отредактируйте сообщение ниже",
    )
    context.bot.send_message(
        chat_id=user_id,
        text="New slots\r\n2023-11-17 10:00\r\n2023-11-20 17:00",
    )
    context.bot.send_message(
        chat_id=user_id,
        text="Для удаления всех слотов за указанный день скопируйте и отредактируйте сообщение ниже",
    )
    context.bot.send_message(
        chat_id=user_id,
        text="Clear days\r\n2023-11-17\r\n2023-11-20",
    )
    context.bot.send_message(
        chat_id=user_id,
        text="Для удаления определенных слотов скопируйте и отредактируйте сообщение ниже",
    )
    context.bot.send_message(
        chat_id=user_id,
        text="Delete slots\r\n2023-11-17 10:00\r\n2023-11-20 17:00",
    )
