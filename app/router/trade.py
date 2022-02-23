from datetime import datetime, timedelta

from fastapi import APIRouter, status, Depends

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.database.conn import db
from app.database.schema import Profiles, Trades, Inventories
from app.models import TradeRegister, Trade


router = APIRouter()


@router.post('/trade', status_code=status.HTTP_201_CREATED, response_model=Trade)
async def trade(request: Request, info: TradeRegister, session: Session = Depends(db.session)):
    owner = Profiles.get(user=request.user.id).id

    # * Item already exists Error
    if await is_exist_item(info.item):
        Exception()

    # * Trade item not owner Error
    if not await is_owner(info.item, owner):
        Exception()

    return Trades.create(session=session, auto_commit=Trade, owner=owner, item=info.item,
                         order_price=info.order_price, immediate_price=info.immediate_price)


@router.get('/trade/{item_id}', status_code=status.HTTP_200_OK, response_model=Trade)
async def get_trade_by_item(item_id: int):
    return Trades.get(item=item_id)


@router.put('/trade/{item_id}/extend', status_code=status.HTTP_200_OK, response_model=Trade)
async def extend_trade_expire(request: Request, item_id: int, extend_days: int = 14):
    owner = Profiles.get(user=request.user.id).id

    # * Trade item not owner Error
    if not await is_owner(item_id, owner=owner):
        Exception()

    target = Trades.get(item=item_id)
    target.expire = target.expire + timedelta(days=extend_days)
    return target


@router.delete('/trade/{item_id}', status_code=status.HTTP_202_ACCEPTED)
async def delete_trade(request: Request, item_id: int):
    owner = Profiles.get(user=request.user.id).id

    # * Trade item not owner Error
    if not await is_owner(item_id, owner=owner):
        Exception()

    target = Trades.get(item=item_id)
    target.delete(auto_commit=True)
    return None


@router.get('/trades', status_code=status.HTTP_200_OK, response_model=list[Trade])
async def get_trades():
    return Trades.filter(expire__gte=datetime.now()).all()


@router.get('/trades/me', status_code=status.HTTP_200_OK, response_model=list[Trade])
async def get_my_trades(request: Request):
    owner = Profiles.get(user=request.user.id).id
    return Trades.filter(owner=owner).all()


async def is_owner(item: int, owner: int):
    if Inventories.get(item=item).owner == owner:
        return True
    return False


async def is_exist_item(item: int):
    if Trades.get(item=item):
        return True
    return False
