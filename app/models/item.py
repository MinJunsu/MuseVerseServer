from datetime import datetime

from pydantic import BaseModel


class ItemBase(BaseModel):
    id: int
    name: str
    author: int
    format: str
    upload: str

    class Config:
        orm_mode = True


class ItemsBase(BaseModel):
    items: list[ItemBase]

    class Config:
        orm_mode = True


class ItemDetailBase(BaseModel):
    id: int
    created_at: datetime
    name: str
    author: str
    format: str
    upload: str

    class Config:
        orm_mode = True
