from datetime import datetime

from pydantic import BaseModel

from app.models.item import ItemDetailBase


class TradeCreate(BaseModel):
    item: int
    price: float


class TradeBase(BaseModel):
    id: int
    seller: int
    item: int
    buyer: int | None
    expire: datetime
    price: float
    is_sell: bool

    class Config:
        orm_mode = True


class TradePriceChange(BaseModel):
    price: float


class TradeDetailBase(BaseModel):
    id: int
    seller: str
    item: ItemDetailBase
    buyer: str | None
    expire: datetime
    price: float
    is_sell: bool

    class Config:
        orm_mode = True


class TradesBase(BaseModel):
    histories: list[TradeDetailBase]

    class Config:
        orm_mode = True
