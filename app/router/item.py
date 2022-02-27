import logging
from datetime import datetime
from fastapi import APIRouter, status, Depends, UploadFile, Form
from sqlalchemy.orm import Session

from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.common.consts import AZURE_STORAGE_KEY, AZURE_STORAGE_ACCESS
from app.database.conn import db
from app.database.schema import Items, Profiles, Inventories, Orders
from app.models import Order, Item, ItemURL, ExhibitionItem
from app.utils.azure_storage import upload_local_file

router = APIRouter()


@router.post('/item', status_code=status.HTTP_201_CREATED, response_model=Item)
async def create_item(request: Request, file: UploadFile, name: str = Form(...),
                      format: str = Form(...), price: float = Form(...), session: Session = Depends(db.session)):
    author = Profiles.get(user=request.user.id).id
    file_name = await upload_local_file(connection_string=AZURE_STORAGE_ACCESS, credential=AZURE_STORAGE_KEY, file=file)
    item = Items.create(session=session, auto_commit=True, name=name, author=author,
                        upload=file_name, format=format, price=price)
    Inventories.create(session=session, auto_commit=True, owner=author, item=item.id)
    return item


@router.get('/item/{item_id}', status_code=status.HTTP_200_OK, response_model=ExhibitionItem)
async def get_item(item_id: int):
    item = Items.get(id=item_id)
    if item is None:
        raise Exception()

    item.author = Profiles.get(id=item.author).nickname

    return item


@router.get('/item/{item_id}/image', status_code=status.HTTP_301_MOVED_PERMANENTLY, response_model=ItemURL)
async def get_item_by_url(item_id: int):
    # * Item does not exists Error
    if Items.filter(id=item_id).count() == 0:
        raise Exception()

    item = Items.get(id=item_id)
    url = f'https://themestorage.blob.core.windows.net/{item.upload}'
    return RedirectResponse(url=url)


@router.get('/items', status_code=status.HTTP_200_OK, response_model=list[Item])
async def get_items():
    return Items.filter().all()
