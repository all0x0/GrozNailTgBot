from sqlalchemy import select
from sqlalchemy.orm import Session

from data.models.user import User


def create_user(session: Session, user: User):
    session.add(user)
    session.commit()
    session.refresh(user)


def get_user(session: Session, chat_id: str):
    query = select(User).filter(User.chat_id == chat_id)
    result = session.execute(query)
    return result.scalar_one_or_none()
