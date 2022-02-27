from datetime import datetime, date, timedelta

from fastapi import APIRouter, status, Depends

from sqlalchemy.orm import Session

from starlette.requests import Request
from starlette.authentication import UnauthenticatedUser

from app.database.schema import Profiles, Inventories, Attendances, Items, Trades, db
from app.models import Profile, Attendance, InventoriesBase, ExhibitionInventories


router = APIRouter()


@router.get('/accounts/me', status_code=status.HTTP_200_OK, response_model=Profile)
async def get_me(request: Request):
    profile = Profiles.get(user=request.user.id)
    items = Items.filter(id__in=[element.item for element in Inventories.filter(
        owner=profile.id).all()]).all()
    profile.inventories = items
    return profile


@router.get('/accounts/inventories', status_code=status.HTTP_200_OK, response_model=InventoriesBase)
async def get_inventories(request: Request):
    profile = Profiles.get(user=request.user.id)
    items = Items.filter(id__in=[element.item for element in Inventories.filter(
        owner=profile.id).all()]).all()
    return {
        'inventories': items
    }


@router.get('/accounts/inventories/exhibition', status_code=status.HTTP_200_OK, response_model=ExhibitionInventories)
async def get_trades(request: Request):
    profile = Profiles.get(user=request.user.id)
    trades = Trades.filter(id__in=[element.item for element in Inventories.filter(
        owner=profile.id).all()]).all()
    for trade in trades:
        trade.item = Items.get(id=trade.item)
    return {
        'exhibitionInventories': trades
    }


@router.post('/accounts/attendance', status_code=status.HTTP_201_CREATED, response_model=Attendance)
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


@router.get('/accounts/attendances', status_code=status.HTTP_200_OK, response_model=list[Attendance])
async def get_attendances(request: Request):
    profile = Profiles.get(user=request.user.id).id
    today = date.today()
    start = date(today.year, today.month, 1)
    end = date(today.year, today.month + 1, 1) if today.month + 1 < 13 else date(today.year + 1, 1, 1)
    return Attendances.filter(profile=profile, attendance_date__range=[start, end]).all()
