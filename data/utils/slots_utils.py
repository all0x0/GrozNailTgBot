from datetime import date, datetime, timedelta

from sqlalchemy import cast, extract, Date, select
from sqlalchemy.orm import Session

from data.models.slot import Slot
from extensions.datetime_extensions import ru_date, ru_datetime


def get_free_slot(session: Session, user_id: int, date_time_slot: datetime):
    query = select(Slot).filter(
        Slot.master_id == user_id, Slot.date_time_slot == date_time_slot
    )
    result = session.execute(query)
    return result.scalar_one_or_none()


def get_free_slots(session: Session, date_time_slot: date):
    query = (
        select(Slot)
        .filter(cast(Slot.date_time_slot, Date) == date_time_slot)
        .order_by(Slot.date_time_slot)
    )
    result = session.execute(query)
    return result.scalars().all()


def get_available_days(session: Session, slot_month: date) -> list[datetime]:
    query = (
        select(Slot.date_time_slot)
        .where(
            extract("month", Slot.date_time_slot) == slot_month.month,
            extract("day", Slot.date_time_slot) > date.today().day
            if datetime.today().month == slot_month.month
            else True,
        )
        .distinct(extract("day", Slot.date_time_slot))
        .order_by(extract("day", Slot.date_time_slot))
    )

    result = session.execute(query)
    return result.scalars().all()


def add_slots(session: Session, user_id: int, dates: list[datetime]) -> list[str]:
    slots_to_write: list[Slot] = []

    if dates:
        for slot in dates:
            existing_slot = get_free_slot(session, user_id, slot)
            if existing_slot is None:
                slots_to_write.append(Slot(master_id=user_id, date_time_slot=slot))

    session.add_all(slots_to_write)
    session.commit()

    return [ru_datetime(slot.date_time_slot) for slot in slots_to_write]


def add_slot(session: Session, user_id: int, date_time_slot: datetime):
    existing_slot = get_free_slot(session, user_id, date_time_slot)

    if existing_slot is None:
        session.add(Slot(master_id=user_id, date_time_slot=date_time_slot))
        session.commit()


def delete_slot(session: Session, user_id: int, date_time_slot: datetime):
    existing_slot = get_free_slot(session, user_id, date_time_slot)

    if existing_slot:
        session.delete(existing_slot)
        session.commit()


def delete_slots(session: Session, user_id: int, dates: list[datetime]):
    slots_to_delete: list[str] = []

    if dates:
        for slot in dates:
            existing_slot = get_free_slot(session, user_id, slot)
            if existing_slot:
                session.delete(existing_slot)
                slots_to_delete.append(ru_datetime(existing_slot.date_time_slot))
    session.commit()
    return slots_to_delete


def clear_days(session: Session, user_id: int, dates: list[datetime]):
    cleared_days: list[str] = []

    if dates:
        for parsed_date in dates:
            session.query(Slot).filter(
                Slot.master_id == user_id,
                Slot.date_time_slot >= parsed_date,
                Slot.date_time_slot < parsed_date + timedelta(days=1),
            ).delete()
            cleared_days.append(ru_date(parsed_date))

    session.commit()
    return cleared_days
