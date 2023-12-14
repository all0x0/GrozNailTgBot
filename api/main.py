import logging

from flask import Flask, request
from telegram import Update
from telegram.ext import (
    CallbackContext,
    Updater,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    Filters,
)

from sqlalchemy.orm import Session

from extensions.command_parser import get_command
from services.calendar_service import get_current_month, get_next_month, get_time_table
from services.main_menu_service import show_main_menu, get_price
from services.greeting_service import send_hello_message, request_user_name, end_of_acquaintance
from services.slot_service import add_new_slots, remove_slots, remove_days, get_hidden_commands
from services.appointment_service import (
    accept_request,
    cancel_appointment,
    get_booked_slots,
    new_appointment,
    reject_request,
)
from config.settings import TOKEN, WEBHOOK_PATH, WEBHOOK_URL
from data.db_setup import get_session
from data.utils.users_utils import get_user
from enums.command import Command

app = Flask("app")

logging.basicConfig(
    format="%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

db: Session = None

application = Updater(token=TOKEN)
unknown_users = {}


def text_message_handler(update: Update, context: CallbackContext):
    if update.message is None:
        return

    if update.message.from_user.is_bot:
        return

    chat_id = get_chat_id(update)
    if chat_id is None:
        return
    message_id = update.message.message_id

    if update.message.text == "/start":
        send_hello_message(db, chat_id, context)
        show_main_menu(db, chat_id, message_id, context)
        return

    if "памагити" in update.message.text.lower():
        get_hidden_commands(db, chat_id, context)
        show_main_menu(db, chat_id, message_id, context)
        return

    if "new slots" in update.message.text.lower():
        add_new_slots(db, chat_id, update.message.text, context)
        show_main_menu(db, chat_id, message_id, context)
        return

    if "delete slots" in update.message.text.lower():
        remove_slots(db, chat_id, update.message.text, context)
        show_main_menu(db, chat_id, message_id, context)
        return

    if "clear days" in update.message.text.lower():
        remove_days(db, chat_id, update.message.text, context)
        show_main_menu(db, chat_id, message_id, context)
        return

    text_to_parse = unknown_users[chat_id]
    if text_to_parse is not None:
        end_of_acquaintance(
            db, update.message.text, update.message.from_user.name, chat_id, context
        )
        command = get_command(text_to_parse)
        new_appointment(db, chat_id, context, command)
        show_main_menu(db, chat_id, None, context)
        del unknown_users[chat_id]
        return

    context.bot.send_message(chat_id=chat_id, text=update.message.text)


def callback_query_handler(update: Update, context: CallbackContext):
    if update.callback_query is None:
        return

    if update.callback_query.from_user.is_bot:
        return

    chat_id = get_chat_id(update)
    if chat_id is None:
        return

    callback_query = update.callback_query
    message_id = callback_query.message.message_id

    try:
        command = get_command(callback_query.data)
        if command.menu:
            if command.menu is Command.MAINMENU:
                show_main_menu(db, chat_id, message_id, context)
                return
            if command.menu is Command.PRICE:
                get_price(db, chat_id, message_id, context)
                return
            if command.menu is Command.AVAILABLE_TIME:
                get_time_table(db, chat_id, message_id, command.date_time, context)
                return
            if command.menu is Command.MASTER_LOCATION:
                # TODO: there is no implementation at all
                pass
            if command.menu is Command.NEW_APPOINTMENT:
                user = get_user(db, chat_id)
                if user is None:
                    unknown_users[chat_id] = callback_query.data
                    request_user_name(chat_id, message_id, context)
                    return
                new_appointment(db, chat_id, context, command)
                show_main_menu(db, chat_id, message_id, context)
                return
            if command.menu is Command.CURRENT_MONTH:
                get_current_month(db, chat_id, message_id, context)
                return
            if command.menu is Command.NEXT_MONTH:
                get_next_month(db, chat_id, message_id, context)
                return
            if command.menu is Command.CANCEL_APPOINTMENT:
                cancel_appointment(db, chat_id, command.date_time, context)
                show_main_menu(db, chat_id, message_id, context)
                return
            if command.menu is Command.CANCEL_APPOINTMENT_LIST:
                get_booked_slots(db, chat_id, message_id, context, Command.CANCEL_APPOINTMENT)
                return
            if command.menu is Command.RESCHEDULE_APPOINTMENT:
                # TODO: there is no implementation at all
                pass
            if command.menu is Command.RESCHEDULE_APPOINTMENT_LIST:
                get_booked_slots(db, chat_id, message_id, context, Command.RESCHEDULE_APPOINTMENT)
                return
            if command.menu is Command.ACCEPT_REQUEST:
                accept_request(db, chat_id, message_id, command, context)
                show_main_menu(db, chat_id, None, context)
                return
            if command.menu is Command.REJECT_REQUEST:
                reject_request(db, chat_id, message_id, command, context)
                show_main_menu(db, chat_id, None, context)
                return
            if command.menu is Command.UNDEFINED:
                pass
    except Exception as e:
        logger.error(
            "callback_query_handler error: %s\nCallback data: %s",
            e,
            callback_query.data,
        )


@app.post(WEBHOOK_PATH)
def bot_webhook():
    try:
        data = request.get_json()
        telegram_update = filters.Update.de_json(data, application.bot)

        if telegram_update is not None:
            global db
            db = get_session()  # TODO: move it to necessary functions into services???

            application.dispatcher.add_handler(
                MessageHandler(Filters.text, text_message_handler)
            )
            application.dispatcher.add_handler(
                CallbackQueryHandler(callback_query_handler)
            )
            application.dispatcher.add_error_handler(error)

            application.dispatcher.process_update(telegram_update)

            return "OK"
    except Exception as e:
        logger.error("bot_webhook error: %s", e)
        return "Error"


def get_chat_id(update: Update) -> int:
    if update.message is not None:
        return update.message.chat_id
    if update.callback_query is not None and update.callback_query.message is not None:
        return update.callback_query.message.chat_id
    return None


@app.get("/")
def index():
    webhook_info = application.bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        application.bot.set_webhook(url=WEBHOOK_URL)
        logger.info("Setting webhook: %s", webhook_info.url)
        return "Webhook has been updated"

    return "Webhook has already been set! I'm ready to work!"


def error(update: Update, context: CallbackContext):
    logger.error("Update %s caused an error:\n%s", update.message, context.error)
