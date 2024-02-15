from datetime import datetime

from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import Session

from data.models.appointment import Appointment


def create_appointment(session: Session, appointment: Appointment):
    session.add(appointment)
    session.commit()
    session.refresh(appointment)


def update_appointment(session: Session, appointment_id: int, **kwargs):
    query = (
        update(Appointment)
        .where(Appointment.id == appointment_id)
        .values(**kwargs)
    )
    session.execute(query)
    session.commit()


def update_reject_appointment(session: Session, appointment_id: int):
    query = (
        update(Appointment)
        .where(Appointment.id == appointment_id)
        .values(is_cancelled=True, is_provided=False)
    )
    session.execute(query)
    session.commit()


def get_user_appointments_time(session: Session, chat_id: int):
    query = (
        select(Appointment.procedure_time)
        .filter(
            and_(
                Appointment.user_id == chat_id,
                or_(
                    Appointment.is_cancelled == False, Appointment.is_cancelled == None
                ),
            )
        )
        .order_by(Appointment.procedure_time)
    )
    result = session.execute(query)
    return result.scalars().all()


def get_appointment(session: Session, chat_id: int):
    query = select(Appointment).filter(
        and_(
            Appointment.user_id == chat_id,
            Appointment.procedure_time >= datetime.utcnow(),
            or_(Appointment.is_cancelled == False, Appointment.is_cancelled == None),
        )
    )
    result = session.execute(query)
    return result.scalar_one_or_none()


def check_appointments_for_master(session: Session, master_id: int):
    query = select(Appointment).filter(
        and_(
            Appointment.master_id == master_id,
            Appointment.procedure_time >= datetime.utcnow(),
            or_(Appointment.is_cancelled == False, Appointment.is_cancelled == None),
        ),
    )
    result = session.execute(query)
    return result.scalars().all()
