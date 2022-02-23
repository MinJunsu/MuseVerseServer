from datetime import datetime

from enum import Enum
from pydantic import BaseModel


class Gender(str, Enum):
    male = "male"
    female = "female"


class UserStatus(str, Enum):
    active = "active"
    deleted = "deleted"
    blocked = "blocked"


class OrderStatus(str, Enum):
    order = "order"
    buy = "buy"


class Token(BaseModel):
    authorization: str


class UserToken(BaseModel):
    id: int
    username: str
    email: str | None
    password: str
    gender: Gender

    class Config:
        orm_mode = True


class ItemBase(BaseModel):
    name: str
    format: str
    price: float = 0


class Item(ItemBase):
    id: int
    author: int
    upload: str

    class Config:
        orm_mode = True


class ItemURL(BaseModel):
    url: str

    class Config:
        orm_mode = True


class UserRegister(BaseModel):
    email: str | None
    username: str
    password: str
    nickname: str
    gender: Gender


class UserLogin(BaseModel):
    username: str
    password: str


class UserBase(BaseModel):
    status: UserStatus
    email: str | None
    username: str
    password: str
    gender: Gender


class Inventory(BaseModel):
    owner: int
    item: int


class Profile(BaseModel):
    id: int
    user: int
    nickname: str
    money: float
    inventories: list[Item] | None

    class Config:
        orm_mode = True


class TradeRegister(BaseModel):
    item: int
    orderPrice: float
    immediatePrice: float


class Trade(BaseModel):
    id: int
    owner: int
    item: int
    expire: datetime
    order_price: float
    immediate_price: float
    is_sell: bool

    class Config:
        orm_mode = True


class OrderRegister(BaseModel):
    item: int
    price: float
    trade: int
    status: OrderStatus = "order"


class Order(BaseModel):
    buyer: int
    item: int
    price: float
    trade: int
    status: OrderStatus

    class Config:
        orm_mode = True


class Attendance(BaseModel):
    profile: int
    attendanceDate: datetime
    status: bool = True

    class Config:
        orm_mode = True
