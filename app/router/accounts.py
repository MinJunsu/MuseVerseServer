from fastapi import APIRouter, status, Depends, HTTPException

from sqlalchemy.orm import Session

from starlette.requests import Request
from starlette.authentication import UnauthenticatedUser

from app.database.conn import db
from app.models.auth import AuthUserProfileBase, AuthProfileBase, AuthRename
from app.models.trade import TradesBase
from app.models.item import ItemsBase
from app.models.exhibition import ExhibitionsBase
from app.models.attendance import AttendanceBase, AttendancesBase
from app.queries.auth import get_user_by_id, get_profile_by_user, modify_profile_nickname, get_profile_nickname_by_id
from app.queries.trade import get_user_buy_history, get_user_sell_history, get_trade_by_id
from app.queries.item import get_user_inventories, get_item_by_id
from app.queries.exhibition import get_user_exhibitions
from app.queries.attendance import get_attendances_by_profile, create_attendance, is_attendance_exist


router = APIRouter()


@router.get('/accounts/me', status_code=status.HTTP_200_OK, response_model=AuthUserProfileBase)
async def get_user_profile(request: Request, session: Session = Depends(db.session)):
    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    user = get_user_by_id(user_id=request.user.id, session=session)
    user.profile = get_profile_by_user(user=request.user.id, session=session)
    return user


@router.put('/accounts/rename', status_code=status.HTTP_200_OK, response_model=AuthProfileBase)
async def modify_nickname(request: Request, info: AuthRename, session: Session = Depends(db.session)):
    if isinstance(request.auth, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    profile = get_profile_by_user(user=request.user.id, session=session)

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Profile does not exist')

    modified_profile = modify_profile_nickname(profile=profile.id, nickname=info.nickname, session=session)
    return modified_profile


@router.get('/accounts/inventories', status_code=status.HTTP_200_OK, response_model=ItemsBase)
async def get_inventories(request: Request, session: Session = Depends(db.session)):
    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    profile = get_profile_by_user(user=request.user.id, session=session)
    items = get_user_inventories(profile=profile.id, session=session)
    return {
        'items': items
    }


@router.get('/accounts/exhibitions', status_code=status.HTTP_200_OK, response_model=ExhibitionsBase)
async def get_exhibitions(request: Request, session: Session = Depends(db.session)):
    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    profile = get_profile_by_user(user=request.user.id, session=session)
    exhibitions = get_user_exhibitions(profile=profile.id, session=session)
    for exhibition in exhibitions:
        exhibition.item = get_item_by_id(exhibition.item, session=session)
        exhibition.item.author = get_profile_nickname_by_id(exhibition.item.author, session=session)
        exhibition.trade = get_trade_by_id(exhibition.trade, session=session)

    return {
        'exhibitions': exhibitions
    }


@router.get('/accounts/history/buy', status_code=status.HTTP_200_OK, response_model=TradesBase)
async def get_my_buy_history(request: Request, session: Session = Depends(db.session)):
    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    profile = get_profile_by_user(user=request.user.id, session=session)
    histories = get_user_buy_history(profile.id, session=session)
    for history in histories:
        history.item = get_item_by_id(history.item, session=session)
    return {
        'histories': histories
    }


@router.get('/accounts/history/sell', status_code=status.HTTP_200_OK, response_model=TradesBase)
async def get_my_sell_history(request: Request, session: Session = Depends(db.session)):
    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    profile = get_profile_by_user(user=request.user.id, session=session)
    histories = get_user_sell_history(profile=profile.id, session=session)
    for history in histories:
        history.item = get_item_by_id(history.item, session=session)
    return {
        'histories': histories
    }


@router.post('/accounts/attendance', status_code=status.HTTP_201_CREATED, response_model=AttendanceBase)
async def post_attendance(request: Request, session: Session = Depends(db.session)):
    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')
    profile = get_profile_by_user(user=request.user.id, session=session)

    if is_attendance_exist(profile=profile.id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Attendance already exists')

    attendance = create_attendance(profile=profile.id, session=session)

    return attendance


@router.get('/accounts/attendances', status_code=status.HTTP_200_OK, response_model=AttendancesBase)
async def get_attendances(request: Request, session: Session = Depends(db.session)):
    profile = get_profile_by_user(user=request.user.id, session=session)
    attendances = get_attendances_by_profile(profile=profile.id, session=session)
    return {
        'attendances': attendances
    }
