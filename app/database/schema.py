from datetime import datetime, timedelta

from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Date, Enum, Boolean, ForeignKey, func
)
from sqlalchemy.orm import Session

from app.database.conn import Base, db


class BaseMixin:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def __init__(self):
        self._q = None
        self._session = None
        self.served = None

    def all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def create(cls, session: Session, auto_commit=False, **kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param session:
        :param auto_commit: 자동 커밋 여부
        :param kwargs: 적재 할 데이터
        :return:
        """
        obj = cls()
        for col in obj.all_columns():
            col_name = col.name
            if col_name in kwargs:
                setattr(obj, col_name, kwargs.get(col_name))
        session.add(obj)
        session.flush()
        if auto_commit:
            session.commit()
        return obj

    @classmethod
    def get(cls, **kwargs) -> object:
        """
        Simply get a Row
        :param kwargs:
        :return:
        """
        session = next(db.session())
        query = session.query(cls)
        for key, val in kwargs.items():
            col = getattr(cls, key)
            query = query.filter(col == val)

        if query.count() > 1:
            raise Exception("Only one row is supposed to be returned, but got more than one.")
        result = query.first()
        session.close()
        return result

    @classmethod
    def filter(cls, session: Session = None, **kwargs) -> object:
        """
        Simply get a Row
        :param session:
        :param kwargs:
        :return:
        """
        cond = []
        for key, val in kwargs.items():
            key = key.split("__")
            if len(key) > 2:
                raise Exception("No 2 more dunders")
            col = getattr(cls, key[0])
            if len(key) == 1: cond.append((col == val))
            elif len(key) == 2 and key[1] == 'gt': cond.append((col > val))
            elif len(key) == 2 and key[1] == 'gte': cond.append((col >= val))
            elif len(key) == 2 and key[1] == 'lt': cond.append((col < val))
            elif len(key) == 2 and key[1] == 'lte': cond.append((col <= val))
            elif len(key) == 2 and key[1] == 'in': cond.append((col.in_(val)))
        obj = cls()
        if session:
            obj._session = session
            obj.served = True
        else:
            obj._session = next(db.session())
            obj.served = False
        query = obj._session.query(cls)
        query = query.filter(*cond)
        obj._q = query
        return obj

    @classmethod
    def cls_attr(cls, col_name=None) -> object:
        if col_name:
            col = getattr(cls, col_name)
            return col
        else:
            return cls

    def order_by(self, *args: str) -> object:
        for a in args:
            if a.startswith("-"):
                col_name = a[1:]
                is_asc = False
            else:
                col_name = a
                is_asc = True
            col = self.cls_attr(col_name)
            self._q = self._q.order_by(col.asc()) if is_asc else self._q.order_by(col.desc())
        return self

    def update(self, auto_commit: bool = False, **kwargs) -> object:
        qs = self._q.update(kwargs)
        get_id = self.id
        ret = None

        self._session.flush()
        if qs > 0:
            ret = self._q.first()
        if auto_commit:
            self._session.commit()
        return ret

    def first(self) -> object:
        result = self._q.first()
        self.close()
        return result

    def delete(self, auto_commit: bool = False) -> None:
        self._q.delete()
        if auto_commit:
            self._session.commit()

    def all(self) -> object:
        print(self.served)
        result = self._q.all()
        self.close()
        return result

    def count(self) -> int:
        result = self._q.count()
        self.close()
        return result

    def close(self) -> None:
        if not self.served:
            self._session.close()
        else:
            self._session.flush()


class Users(Base, BaseMixin):
    __tablename__ = 'users'
    status = Column(Enum('active', 'deleted', 'blocked', name='user_status'), default='active')
    # TODO: needs email validator
    email = Column(String(length=100), nullable=True)
    username = Column(String(length=50), nullable=False)
    password = Column(String(length=200), nullable=False)
    gender = Column(Enum('male', 'female', name='gender_status'), default='male')


class Profiles(Base, BaseMixin):
    __tablename__ = 'profiles'
    user = Column(Integer, ForeignKey('users.id'), nullable=False)
    nickname = Column(String(length=100), nullable=True)
    money = Column(Float, default=0)


class Items(Base, BaseMixin):
    __tablename__ = 'items'
    name = Column(String(length=50), nullable=False)
    author = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    # ! 특정한 포맷이 정해진다면 enum 타입으로 변환
    # format = Column(Enum('type1', 'type2'), default='type1')
    format = Column(String(length=30), nullable=False)
    # TODO: needs URL validator
    upload = Column(String(length=200), nullable=False)
    price = Column(Float, default=0)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)


class Inventories(Base, BaseMixin):
    __tablename__ = 'inventories'
    owner = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    item = Column(Integer, ForeignKey('items.id'), nullable=False)


class Trades(Base, BaseMixin):
    __tablename__ = 'trades'
    owner = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    item = Column(Integer, ForeignKey('items.id'), nullable=False)
    expire = Column(DateTime, default=datetime.now() + timedelta(days=14), nullable=True)
    order_price = Column(Float, default=0)
    immediate_price = Column(Float, default=0)
    is_sell = Column(Boolean, default=True)


class Orders(Base, BaseMixin):
    __tablename__ = 'orders'
    buyer = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    item = Column(Integer, ForeignKey('items.id'), nullable=False)
    trade = Column(Integer, ForeignKey('trades.id'), nullable=False)
    price = Column(Float, default=0)
    status = Column(Enum('order', 'buy', name='order_status'), default='order')


class Exhibitions(Base, BaseMixin):
    __tablename__ = 'exhibitions'
    hall = Column(Enum('First', 'Second', 'Third', name='hall'), nullable=False)
    trade = Column(Integer, ForeignKey('trades.id'), nullable=True)
    num = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    expire = Column(DateTime, nullable=True)
    max_width = Column(Integer, default=640)
    max_height = Column(Integer, default=480)


class Attendances(Base, BaseMixin):
    __tablename__ = 'attendances'
    profile = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    attendance_date = Column(Date, nullable=False)


class PrivateRooms(Base, BaseMixin):
    __tablename__ = 'private_rooms'
    num = Column(Integer, nullable=True)
    inventory = Column(Integer, ForeignKey('inventories.id'), nullable=False)


# TODO: ADD schema EventReceiveLog -> 거의 사용 안할 것으로 보임.
