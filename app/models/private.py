from pydantic import BaseModel

from app.models.item import ItemDetailBase


class PrivateExhibitionCreate(BaseModel):
    item: int
    num: int


class PrivateExhibitionBase(BaseModel):
    id: int
    item: int
    num: int

    class Config:
        orm_mode = True


class PrivateExhibitionDetailBase(BaseModel):
    owner: str
    item: ItemDetailBase

    class Config:
        orm_mode = True
