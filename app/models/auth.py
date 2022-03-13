from datetime import datetime

from enum import Enum
from pydantic import BaseModel


class AuthLogin(BaseModel):
    username: str
    password: str


class AuthUserCreate(BaseModel):
    username: str
    password: str
    email: str
    nickname: str


class AuthRename(BaseModel):
    nickname: str


class AuthUserBase(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True


class AuthProfileBase(BaseModel):
    id: int
    nickname: str
    money: float

    class Config:
        orm_mode = True


class AuthUserProfileBase(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    username: str
    email: str
    profile: AuthProfileBase

    class Config:
        orm_mode = True


class TokenBase(BaseModel):
    authorization: str

    class Config:
        orm_mode = True
