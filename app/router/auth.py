import bcrypt
import jwt
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.orm import Session
from starlette.authentication import UnauthenticatedUser
from starlette.requests import Request

from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.schema import db
from app.models.auth import (
    AuthLogin, AuthUserCreate, AuthUserBase, TokenBase
)
from app.queries.auth import (
    get_user_by_username, is_username_exist, create_user, create_profile
)


router = APIRouter()


@router.post('/auth/login', status_code=status.HTTP_200_OK, response_model=TokenBase)
async def login(info: AuthLogin, session: Session = Depends(db.session)):
    if not is_username_exist(info.username, session=session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')

    user = get_user_by_username(username=info.username, session=session)
    is_verified = bcrypt.checkpw(info.password.encode("UTF-8"), user.password.encode("UTF-8"))

    print(f"UserInfo: {info}")
    # * Password not equal Error
    if not is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Password does not match')

    return dict(
        authorization=f"Bearer {create_access_token(data=AuthUserBase.from_orm(user).dict(), expires_delta=24)}"
    )


@router.post('/auth/register', status_code=status.HTTP_201_CREATED, response_model=TokenBase)
async def register(info: AuthUserCreate, session: Session = Depends(db.session)):
    if not info.username or not info.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You have to send all params')

    info.password = bcrypt.hashpw(info.password.encode('UTF-8'), bcrypt.gensalt()).decode('UTF-8')
    user = create_user(info=info, session=session)
    create_profile(user=user.id, nickname=info.nickname, session=session)

    return dict(
        authorization="Bearer " + create_access_token(data=AuthUserBase.from_orm(user).dict(), expires_delta=24)
    )


def create_access_token(*, data: dict = None, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.now() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt
