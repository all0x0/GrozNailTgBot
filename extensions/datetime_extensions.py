from datetime import datetime

russian_weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
russian_months = [
    "",
    "Янв",
    "Фев",
    "Мар",
    "Апр",
    "Май",
    "Июн",
    "Июл",
    "Авг",
    "Сен",
    "Окт",
    "Ноя",
    "Дек",
]


def ru_date(dt: datetime):
    """_summary_
    converts a datetime to a string Format: "%Y-%m-%d"
    """
    return dt.strftime("%Y-%m-%d")


def ru_time(dt: datetime):
    """_summary_
    converts a datetime to a string Format: "%H:%M"
    """
    return dt.strftime("%H:%M")


def ru_datetime(dt: datetime):
    """_summary_
    converts a datetime to a string Format: "%Y-%m-%d %H:%M"
    """
    return dt.strftime("%Y-%m-%d %H:%M")


def represent_datetime(dt: datetime):
    """_summary_
    converts a datetime to a string Format: "%d.%m.%Y (%a) - %H:%M"
    """
    return dt.strftime("%d.%m.%Y (weekday) - %H:%M").replace(
        "weekday", russian_weekdays[dt.weekday()]
    )


def represent_date_only(dt: datetime):
    """_summary_
    converts a datetime to a string Format: "%b %Y"
    """
    return dt.strftime("month %Y").replace("month", russian_months[dt.month])


def try_parse_dates(dates_to_parse: str, date_format="%Y-%m-%d %H:%M"):
    string_dates = dates_to_parse.split("\n")
    if len(string_dates) == 0:
        return []
    result: list[datetime] = []

    for string_date in string_dates[1:]:
        parsed_datetime = try_parse_datetime(string_date, date_format)
        if parsed_datetime:
            result.append(parsed_datetime)

    return result


def try_parse_datetime(string_slot: str, date_format="%Y-%m-%d %H:%M"):
    try:
        parsed_datetime = datetime.strptime(string_slot.strip(), date_format)
        return parsed_datetime
    except ValueError:
        return None


def add_months(current_date: datetime, months_to_add: datetime):
    new_date = datetime(
        current_date.year + (current_date.month + months_to_add - 1) // 12,
        (current_date.month + months_to_add - 1) % 12 + 1,
        current_date.day,
        current_date.hour,
        current_date.minute,
        current_date.second,
    )
    return new_date
