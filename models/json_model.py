from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field
import numpy as np


class Workers(BaseModel):
    event: str
    day_night: str
    work_time: float
    work_calendar_day: int
    work_calendar_daytype: int
    job_name: str
    job_department: str
    job_position: str
    period_month: str
    period_year: int
    kontrakt_name: str

    kontrakt_type: Optional[Union[str, int]] = 0
    kontrakt_issuecount: Optional[int] = 0
    kontrakt_filter: Optional[str] = "0"
    kontrakt_timetracking: Union[Dict[str, list], float]


class Clock(BaseModel):
    event: str
    day_night: str
    work_time: float
    work_calendar_day: int
    work_calendar_daytype: int
    job_name: str
    job_department: str
    job_position: str
    period_month: str
    period_year: int
    kontrakt_name: str

    kontrakt_issuecount: Optional[int] = 0
    kontrakt_filter: Optional[str] = "0"
    kontrakt_timetracking: Optional[float] = 0.0


class MonthYear(BaseModel):
    month: str
    year: int


class Worker(BaseModel):
    name: str
    department: str
    position: str


class WorkDay(BaseModel):
    day: int
    daytype: int


class Kontrakt(BaseModel):
    name: str
    issuecount: Optional[str] = 0
    timetracking: Optional[List[Dict[str, list]]] = {'0': [0, 0]}
    filter: Optional[str] = '0'


class Days(BaseModel):
    work_calendar: WorkDay
    kontrakt: List[Kontrakt]
    event: str
    day_night: str
    work_time: float


class Raw(BaseModel):
    period: Dict[str, str]
    job: Dict[str, str]
    days: List[Days]


