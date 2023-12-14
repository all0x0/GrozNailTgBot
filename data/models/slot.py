from sqlalchemy import Column, DateTime, Integer, BigInteger

from data.mixins import Timestamp
from data.db_setup import Base


class Slot(Timestamp, Base):
    __tablename__ = "slots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    master_id = Column(BigInteger)
    external_master_id = Column(Integer)
    date_time_slot = Column(DateTime)
