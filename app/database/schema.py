from datetime import date, datetime, timedelta

from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Date, Enum, Boolean, ForeignKey, func
)
from sqlalchemy.orm import Session

from app.database.conn import Base, db


class BaseMixin:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = Column(Boolean, default=False)


class Users(Base, BaseMixin):
    def __init__(self, username: str, password: str, email: str):
        super(Users, self).__init__()
        self.username = username
        self.password = password
        self.email = email

    __tablename__ = 'users'
    status = Column(Enum('active', 'deleted', 'blocked', name='user_status'), default='active')
    email = Column(String(length=100), nullable=True)
    username = Column(String(length=50), nullable=False)
    password = Column(String(length=200), nullable=False)


class Profiles(Base, BaseMixin):
    def __init__(self, user: int, nickname: str, money: float):
        super(Profiles, self).__init__()
        self.user = user
        self.nickname = nickname
        self.money = money

    __tablename__ = 'profiles'
    user = Column(Integer, ForeignKey('users.id'), nullable=False)
    nickname = Column(String(length=100), nullable=True)
    money = Column(Float, default=0)


class Items(Base, BaseMixin):
    def __init__(self, name: str, author: int | str, upload: str, file_format: str):
        self.name = name
        self.author = author
        self.upload = upload
        self.format = file_format

    __tablename__ = 'items'
    name = Column(String(length=50), nullable=False)
    author = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    format = Column(String(length=30), nullable=False)
    upload = Column(String(length=200), nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)


class Inventories(Base, BaseMixin):
    def __init__(self, owner: int, item: int):
        self.owner = owner
        self.item = item

    __tablename__ = 'inventories'
    owner = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    item = Column(Integer, ForeignKey('items.id'), nullable=False)


class Trades(Base, BaseMixin):
    def __init__(self, seller: int, item: int, price: float):
        self.seller = seller
        self.item = item
        self.price = price

    __tablename__ = 'trades'
    seller = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    item = Column(Integer, ForeignKey('items.id'), nullable=False)
    buyer = Column(Integer, ForeignKey('profiles.id'), nullable=True)
    expire = Column(DateTime, default=datetime.now() + timedelta(days=14), nullable=True)
    price = Column(Float, default=0)
    is_sell = Column(Boolean, default=False)


class Exhibitions(Base, BaseMixin):
    def __init__(self, item: int, owner: int, trade: int, hall: int, num: int):
        self.item = item
        self.owner = owner
        self.trade = trade
        self.hall = hall
        self.num = num
        self.expire = datetime.now() + timedelta(days=14)

    __tablename__ = 'exhibitions'
    item = Column(Integer, ForeignKey('items.id'), nullable=False)
    owner = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    trade = Column(Integer, ForeignKey('trades.id'), nullable=True)
    hall = Column(Integer, nullable=False)
    num = Column(Integer, nullable=False)
    expire = Column(DateTime, nullable=True)
    max_width = Column(Integer, default=640)
    max_height = Column(Integer, default=480)


class Attendances(Base, BaseMixin):
    def __init__(self, profile: int):
        self.profile = profile
        self.attendance_date = date.today()

    __tablename__ = 'attendances'
    profile = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    attendance_date = Column(Date, nullable=False)


class PrivateRooms(Base, BaseMixin):
    def __init__(self, owner: int, item: int, num: int):
        self.owner = owner
        self.item = item
        self.num = num

    __tablename__ = 'private_rooms'
    owner = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    item = Column(Integer, ForeignKey('items.id'), nullable=False)
    num = Column(Integer, nullable=True)
    max_width = Column(Integer, default=640)
    max_height = Column(Integer, default=480)


# TODO: ADD schema EventReceiveLog -> 거의 사용 안할 것으로 보임.
