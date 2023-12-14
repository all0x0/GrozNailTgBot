from sqlalchemy import (
    Column,
    Boolean,
    DateTime,
    Integer,
    DECIMAL,
    BigInteger,
    Enum,
)

from data.mixins import Timestamp
from data.db_setup import Base

from enums.package import Package


class Appointment(Timestamp, Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    master_id = Column(BigInteger)
    user_id = Column(BigInteger)
    package_type = Column(Enum(Package), default=Package.UNDEFINED)
    procedure_time = Column(DateTime)
    is_confirmed = Column(Boolean, nullable=True, default=None)
    is_provided = Column(Boolean, nullable=True, default=None)
    is_cancelled = Column(Boolean, nullable=True, default=None)
    elapsed_time = Column(DateTime, nullable=True, default=None)
    final_cost = Column(DECIMAL, nullable=True, default=None)
