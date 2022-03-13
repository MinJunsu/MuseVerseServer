from fastapi import APIRouter, status, Depends, Request, HTTPException
from fastapi.security import APIKeyHeader

from sqlalchemy.orm import Session
from starlette.authentication import UnauthenticatedUser
from starlette.responses import RedirectResponse

from app.common.consts import UPLOAD_IMAGE
from app.database.conn import db
from app.models.exhibition import ExhibitionCreate, ExhibitionBase, ExhibitionDetailBase
from app.queries.auth import get_profile_by_user, get_profile_nickname_by_id
from app.queries.item import get_item_by_id
from app.queries.trade import create_or_get_trade, get_trade_by_id
from app.queries.exhibition import (
    is_exhibition_exists, is_item_exhibit, is_number_exists, is_exhibition_owner, create_exhibition,
    modify_exhibition_expire, get_exhibition_by_hall_num, remove_exhibition
)


router = APIRouter()


@router.post('/exhibition', status_code=status.HTTP_201_CREATED, response_model=ExhibitionBase, dependencies=[Depends(
    APIKeyHeader(name="Authorization", auto_error=False))])
async def post_exhibition(request: Request, info: ExhibitionCreate, session: Session = Depends(db.session)):
    owner = get_profile_by_user(user=request.user.id, session=session)

    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    if is_number_exists(hall=info.hall, num=info.num, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Hall & Num already exist')

    if is_item_exhibit(item=info.item, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Item already exhibit')

    trade = create_or_get_trade(item=info.item, seller=owner.id, price=info.price, session=session)

    exhibition = create_exhibition(info=info, owner=owner.id, trade=trade.id, session=session)
    return exhibition


@router.put('/exhibition/{exhibition_id}/extend', status_code=status.HTTP_202_ACCEPTED, response_model=ExhibitionBase,
            dependencies=[Depends(APIKeyHeader(name="Authorization", auto_error=False))])
async def put_exhibition_extend(request: Request, exhibition_id: int, session: Session = Depends(db.session)):
    owner = get_profile_by_user(user=request.user.id, session=session)

    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    if not is_exhibition_exists(exhibition=exhibition_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Exhibition does not exist')

    if not is_exhibition_owner(exhibition=exhibition_id, owner=owner.id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You can not extend')

    # * 유효기간이 3일 이내로 남았을 경우에만 연장

    exhibition = modify_exhibition_expire(exhibition=exhibition_id, session=session)
    return exhibition


@router.delete('/exhibition/{exhibition_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(
    APIKeyHeader(name="Authorization", auto_error=False))])
async def delete_exhibition(request: Request, exhibition_id: int, session: Session = Depends(db.session)):
    owner = get_profile_by_user(user=request.user.id, session=session)

    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    if not is_exhibition_exists(exhibition=exhibition_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Exhibition does not exist')

    if not is_exhibition_owner(exhibition=exhibition_id, owner=owner, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You can not extend')

    exhibition = remove_exhibition(exhibition=exhibition_id, session=session)
    return None


@router.get('/exhibition/{hall}/{num}', status_code=status.HTTP_200_OK, response_model=ExhibitionDetailBase)
async def get_exhibition(hall: int, num: int, session: Session = Depends(db.session)):
    if not is_number_exists(hall=hall, num=num, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Hall & Num does not exist')

    exhibition = get_exhibition_by_hall_num(hall=hall, num=num, session=session)
    exhibition.item = get_item_by_id(item=exhibition.item, session=session)
    exhibition.trade = get_trade_by_id(trade=exhibition.trade, session=session)
    exhibition.owner = get_profile_nickname_by_id(profile=exhibition.owner, session=session)
    return exhibition


@router.get('/exhibition/{hall}/{num}/image', status_code=status.HTTP_301_MOVED_PERMANENTLY)
async def get_exhibition_image(hall: int, num: int, session: Session = Depends(db.session)):
    if not is_number_exists(hall=hall, num=num, session=session):
        return RedirectResponse(url=UPLOAD_IMAGE)

    exhibition = get_exhibition_by_hall_num(hall=hall, num=num, session=session)

    item = get_item_by_id(item=exhibition.item, session=session)
    return RedirectResponse(url=f'https://themestorage.blob.core.windows.net/{item.upload}')
