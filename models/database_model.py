from sqlalchemy import ForeignKey, String, Column, Integer, JSON, BIGINT, VARCHAR

from database.sql import Base
from sqlalchemy.orm import mapped_column, Mapped


class RawJS(Base):
    __tablename__ = 'raw_js'
    id: Mapped[str] = mapped_column(String(1000), primary_key=True)
    job_name: Mapped[str] = mapped_column(String(50))
    job_department: Mapped[str] = mapped_column(String(255))
    job_position: Mapped[str] = mapped_column(String(255))
    period_month: Mapped[str] = mapped_column(String(10))
    period_year: Mapped[int]
    json_worker: Mapped[JSON] = mapped_column(type_=JSON)


class ClockJS(Base):
    __tablename__ = 'clock_js'
    id: Mapped[str] = mapped_column(String(1000), primary_key=True)
    job_name: Mapped[str] = mapped_column(String(50))
    job_department: Mapped[str] = mapped_column(String(255))
    job_position: Mapped[str] = mapped_column(String(255))
    period_month: Mapped[str] = mapped_column(String(10))
    period_year: Mapped[int]
    json_worker: Mapped[JSON] = mapped_column(type_=JSON)
