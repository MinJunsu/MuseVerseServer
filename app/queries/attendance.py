from datetime import date

from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.conn import db
from app.database.schema import Attendances


def is_attendance_exist(profile: int, session: Session) -> bool:
    session = next(db.session())
    return session.query(session.query(Attendances).filter(
        Attendances.profile == profile, Attendances.attendance_date == date.today()).exists()).scalar()


def get_attendances_by_profile(profile: int, session: Session) -> list[Attendances]:
    session = next(db.session())
    year = date.today().year
    month = date.today().month
    return session.query(Attendances).filter(
        Attendances.profile == profile, Attendances.attendance_date >= f'{year}-{month}-01',
        Attendances.attendance_date <= f'{year}-{month + 1}-01').all()


def create_attendance(profile: int, session: Session) -> Attendances:
    session = next(db.session())
    attendance = Attendances(profile=profile)
    session.add(attendance)
    session.commit()
    return attendance
