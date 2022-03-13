from datetime import date

from pydantic import BaseModel


class AttendanceBase(BaseModel):
    profile: int
    attendance_date: date

    class Config:
        orm_mode = True


class AttendancesBase(BaseModel):
    attendances: list[AttendanceBase]

    class Config:
        orm_mode = True
