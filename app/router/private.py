from fastapi import APIRouter, status, Depends, HTTPException

from sqlalchemy.orm import Session

from starlette.requests import Request

from app.database.conn import db
from app.models.private import PrivateExhibitionBase, PrivateExhibitionCreate, PrivateExhibitionDetailBase
from app.queries.auth import get_profile_by_user, get_profile_nickname_by_id
from app.queries.item import is_item_owner, get_item_by_id
from app.queries.private import (
    is_num_exists, create_private_exhibition, is_private_exists, is_private_owner, remove_private_exhibition,
    get_private_exhibition
)


router = APIRouter()


@router.post('/private', status_code=status.HTTP_201_CREATED, response_model=PrivateExhibitionBase)
async def post_private(request: Request, info: PrivateExhibitionCreate, session: Session = Depends(db.session)):
    owner = get_profile_by_user(user=request.user.id, session=session)

    if not is_item_owner(owner=owner.id, item=info.item, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You can not exhibit other item')

    if is_num_exists(num=info.num, owner=owner.id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Num already used')

    private_exhibition = create_private_exhibition(info=info, owner=owner.id, session=session)
    return private_exhibition


@router.get('/private/{private_id}', status_code=status.HTTP_200_OK, response_model=PrivateExhibitionDetailBase)
async def get_private_detail(private_id: int, session: Session = Depends(db.session)):
    if not is_private_exists(private=private_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Private Exhibition does not exist')

    private_exhibition = get_private_exhibition(private=private_id, session=session)
    private_exhibition.item = get_item_by_id(item=private_exhibition.item, session=session)
    private_exhibition.owner = get_profile_nickname_by_id(profile=private_exhibition.owner, session=session)
    return private_exhibition


@router.delete('/private/{private_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_private(request: Request, private_id: int, session: Session = Depends(db.session)):
    owner = get_profile_by_user(user=request.user.id, session=session)

    if not is_private_owner(private=private_id, owner=owner.id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You can not delete other private')

    if not is_private_exists(private=private_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Private Exhibition does not exist')

    private_exhibition = remove_private_exhibition(private=private_id, session=session)
    return None


