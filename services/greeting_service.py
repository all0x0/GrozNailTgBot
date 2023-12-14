from telegram.ext import CallbackContext

from sqlalchemy.orm import Session

from enums.role import Role
from data.models.user import User
from data.utils.users_utils import get_user, create_user

INSTRUCTION = "your instructions here..."


def send_hello_message(db: Session, user_id: int, context: CallbackContext):
    existingUser = get_user(db, user_id)

    if existingUser is None:
        context.bot.send_message(
            chat_id=user_id, text=f"Добро пожаловать!"#\n{INSTRUCTION}"
        )
        return

    context.bot.send_message(
        chat_id=user_id,
        text=f"С возвращением {existingUser.name}!\n"
        #+ f"На всякий случай, инструкция:\n{INSTRUCTION}",
    )


def request_user_name(chat_id: int, message_id: int, context: CallbackContext):
    context.bot.send_message(
        chat_id=chat_id,
        text="Как я могу к вам обращаться? Просто отправьте свое имя в сообщении",
    )
    context.bot.delete_message(chat_id=chat_id, message_id=message_id)


def end_of_acquaintance(
    session: Session,
    name: str,
    telegram_user_name: str,
    chat_id: int,
    context: CallbackContext,
):
    if name:
        user = User(
            chat_id=chat_id,
            name=name.strip(),
            role=Role.USER,
            telegram=telegram_user_name,
        )
        create_user(session, user)
        context.bot.send_message(
            chat_id=chat_id, text=f"Приятно познакомиться, {name.strip()}!"
        )
