from datetime import datetime, date, timedelta

from fastapi import APIRouter, status, Depends

from sqlalchemy.orm import Session

from starlette.requests import Request
from starlette.authentication import UnauthenticatedUser

from app.database.schema import Profiles, Inventories, Attendances, Items, db
from app.models import Profile, Attendance


router = APIRouter()


@router.get('/accounts/me', status_code=status.HTTP_200_OK, response_model=Profile)
async def get_me(request: Request):
    profile = Profiles.get(user=request.user.id)
    items = Items.filter(id__in=[element.item for element in Inventories.filter(
        owner=Profiles.get(user=request.user.id).id).all()]).all()
    profile.inventories = items
    return profile


@router.post('accounts/attendance', status_code=status.HTTP_201_CREATED, response_model=Attendance)
async def create_attendance(request: Request, session: Session = Depends(db.session)):
    # * UnauthenticatedUser Error
    if isinstance(request.user, UnauthenticatedUser):
        Exception()
    profile = Profiles.get(user=request.user.id).id
    today = date.today()

    # * Already exists Error
    if Attendances.filter(profile=profile, attendance_date=today).count() > 0:
        raise Exception()

    return Attendances.create(session=session, auto_commit=True, profile=profile, attendance_date=today)


@router.get('accounts/attendances', status_code=status.HTTP_200_OK, response_model=list[Attendance])
async def get_attendances(request: Request):
    profile = Profiles.get(user=request.user.id).id
    today = date.today()
    start = date(today.year, today.month, 1)
    end = date(today.year, today.month + 1, 1) if today.month + 1 < 13 else date(today.year + 1, 1, 1)
    return Attendances.filter(profile=profile, attendance_date__range=[start, end]).all()
