from datetime import datetime

from extensions.datetime_extensions import try_parse_datetime
from enums.command import Command


def get_command(text_to_parse: str):
    text_parts = text_to_parse.split("__")
    menu_command: Command = None
    additional_command: Command = None
    date_time: datetime = None
    user_id: int = None

    if text_parts:
        if text_parts[0].upper() in Command.__members__:
            menu_command = Command[text_parts[0].upper()]
        if len(text_parts) > 1:
            additional_command = Command[text_parts[1].upper()]
        if len(text_parts) > 2:
            date_time = try_parse_datetime(text_parts[2])
        if len(text_parts) > 3:
            try:
                user_id = int(text_parts[3])
            except ValueError:
                pass
    return ComplexCommand(menu_command, additional_command, date_time, user_id)


class ComplexCommand:
    def __init__(
        self,
        menu: Command,
        additional_command: Command,
        date_time: datetime,
        user_id: int,
    ):
        self.menu = menu
        self.additional_command = additional_command
        self.date_time = date_time
        self.user_id = user_id
