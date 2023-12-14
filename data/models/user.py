from sqlalchemy import Column, Integer, BigInteger, String, Enum

from data.mixins import Timestamp
from data.db_setup import Base

from enums.role import Role
from enums.loyalty import Loyalty


class User(Timestamp, Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150))
    chat_id = Column(BigInteger, index=True, unique=True)
    role = Column(Enum(Role), default=0)
    external_id = Column(Integer, nullable=True, unique=True, default=None)
    phone_number = Column(String(50), nullable=True, default=None)
    whatsApp = Column(String(50), nullable=True, default=None)
    telegram = Column(String(50), nullable=True, default=None)
    email = Column(String(50), nullable=True, default=None)
    loyal_level = Column(Enum(Loyalty), default=0)
