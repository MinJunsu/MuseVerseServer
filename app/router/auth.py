import bcrypt
import jwt
from datetime import datetime, date, timedelta

from fastapi import APIRouter, Depends
from fastapi import status

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.schema import Users, Profiles, Attendances, db
from app.models import UserRegister, Token, UserToken, UserLogin, Attendance


router = APIRouter()


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=Token)
async def register(info: UserRegister, session: Session = Depends(db.session)):
    is_exist = await is_username_exist(info.username)

    # * Username or Password input Error
    if not info.username or not info.password:
        raise Exception()

    # * User already exists Error
    if is_exist:
        raise Exception()

    hashed_password = bcrypt.hashpw(info.password.encode('UTF-8'), bcrypt.gensalt()).decode('UTF-8')
    user = Users.create(session=session, auto_commit=True, username=info.username, password=hashed_password)
    create_profile(user=user.id, nickname=info.nickname, money=0, session=session)

    return dict(
        Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(user).dict(exclude={'pw'}), )}")


@router.post('/login', status_code=status.HTTP_200_OK, response_model=Token)
async def login(info: UserLogin):
    is_exist = await is_username_exist(info.username)

    # * User not exists Error
    if not is_exist:
        Exception()
    user = Users.get(username=info.username)
    is_verified = bcrypt.checkpw(info.password.encode("UTF-8"), user.password.encode("UTF-8"))

    # * Password not equal Error
    if not is_verified:
        Exception()

    return dict(
        authorization=f"Bearer {create_access_token(data=UserToken.from_orm(user).dict(exclude={'password', 'gender'}), expires_delta=24)}"
    )


def create_profile(user: int, nickname: str, money: float, session: Session):
    profile = Profiles.create(session=session, auto_commit=True, user=user, nickname=nickname, money=money)
    if profile:
        return True
    return False


async def is_username_exist(username: str):
    if Users.get(username=username):
        return True
    return False


def create_access_token(*, data: dict = None, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.now() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt
