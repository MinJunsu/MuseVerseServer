import logging
from datetime import datetime
from fastapi import APIRouter, status, Depends, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
from starlette.authentication import UnauthenticatedUser

from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.common.consts import AZURE_STORAGE_KEY, AZURE_STORAGE_ACCESS
from app.database.conn import db
from app.models.item import ItemBase, ItemDetailBase
from app.queries.auth import get_profile_by_user, get_profile_by_id, get_profile_nickname_by_id
from app.queries.item import (
    create_item, create_inventory, is_item_exists, get_item_by_id, is_item_owner,
    remove_item
)
from app.utils.azure_storage import upload_local_file

router = APIRouter()


@router.post('/item', status_code=status.HTTP_201_CREATED, response_model=ItemBase)
async def post_item(request: Request, file: UploadFile, name: str = Form(...),
                    file_format: str = Form(...), session: Session = Depends(db.session)):
    author = get_profile_by_user(user=request.user.id, session=session)

    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    file_name = await upload_local_file(connection_string=AZURE_STORAGE_ACCESS, credential=AZURE_STORAGE_KEY, file=file)

    item = create_item(name=name, author=author.id, upload=file_name, file_format=file_format, session=session)
    create_inventory(owner=author.id, item=item.id, session=session)
    return item


@router.get('/item/{item_id}', status_code=status.HTTP_200_OK, response_model=ItemDetailBase)
async def get_item(item_id: int, session: Session = Depends(db.session)):
    if not is_item_exists(item=item_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Item does not exist')

    item = get_item_by_id(item=item_id, session=session)
    item.author = get_profile_nickname_by_id(profile=item.author, session=session)
    return item


@router.delete('/item/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(request: Request, item_id: int, session: Session = Depends(db.session)):
    owner = get_profile_by_user(user=request.user.id, session=session)
    if not is_item_exists(item=item_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Item does not exist')

    if not is_item_owner(owner=owner.id, item=item_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You can not delete item')

    item = remove_item(item=item_id, session=session)
    return None


@router.get('/item/{item_id}/image', status_code=status.HTTP_301_MOVED_PERMANENTLY)
async def get_item_image(item_id: int, session: Session = Depends(db.session)):
    if not is_item_exists(item=item_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Item does not exist')

    item = get_item_by_id(item=item_id, session=session)
    return RedirectResponse(url=f'https://themestorage.blob.core.windows.net/{item.upload}')
