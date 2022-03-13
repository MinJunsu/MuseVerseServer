from datetime import datetime

from pydantic import BaseModel

from app.models.item import ItemBase, ItemDetailBase
from app.models.trade import TradeBase, TradeDetailBase


class ExhibitionCreate(BaseModel):
    item: int
    price: float
    hall: int
    num: int


class ExhibitionBase(BaseModel):
    id: int
    item: int
    trade: int
    owner: int
    hall: int
    num: int
    expire: datetime

    class Config:
        orm_mode = True


class ExhibitionDetailBase(BaseModel):
    id: int
    item: ItemDetailBase
    trade: TradeBase
    owner: str
    expire: datetime

    class Config:
        orm_mode = True


class ExhibitionsBase(BaseModel):
    exhibitions: list[ExhibitionDetailBase]

    class Config:
        orm_mode = True
