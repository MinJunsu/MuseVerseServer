from fastapi import APIRouter, status, Depends, HTTPException

from sqlalchemy.orm import Session
from starlette.authentication import UnauthenticatedUser
from starlette.requests import Request

from app.database.conn import db
from app.models.trade import TradeCreate, TradeBase, TradeDetailBase, TradesBase, TradePriceChange
from app.queries.auth import get_profile_by_user, get_profile_nickname_by_id
from app.queries.exhibition import remove_exhibition, get_exhibition_by_trade
from app.queries.item import get_item_by_id, modify_inventory
from app.queries.trade import (
    is_item_exist, is_trade_exist, is_seller, create_trade, extend_trade_expire, get_trade_by_id, get_trade_list,
    buy_trade_item, remove_trade, change_trade_price
)
from app.queries.item import is_item_owner


router = APIRouter()


@router.post('/trade', status_code=status.HTTP_201_CREATED, response_model=TradeBase)
async def post_trade(request: Request, info: TradeCreate, session: Session = Depends(db.session)):
    seller = get_profile_by_user(user=request.user.id, session=session)

    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    if is_item_exist(item=info.item, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Item already exists')

    if not is_item_owner(owner=seller.id, item=info.item, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Trade item not owner')

    trade = create_trade(info=info, seller=seller.id, session=session)
    return trade


@router.get('/trade/{trade_id}', status_code=status.HTTP_200_OK, response_model=TradeDetailBase)
async def get_trade(trade_id: int, session: Session = Depends(db.session)):
    if not is_trade_exist(trade=trade_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Trade does not exist')

    trade = get_trade_by_id(trade=trade_id, session=session)
    trade.seller = get_profile_nickname_by_id(profile=trade.seller, session=session)
    trade.buyer = get_profile_nickname_by_id(profile=trade.buyer, session=session)
    trade.item = get_item_by_id(item=trade.item, session=session)
    return trade


@router.delete('/trade/{trade_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_trade(request: Request, trade_id: int, session: Session = Depends(db.session)):
    owner = get_profile_by_user(user=request.user.id, session=session)

    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    if not is_trade_exist(trade=trade_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Trade does not exist')

    if not is_seller(trade=trade_id, buyer=owner.id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Can not delete other trade')

    trade = remove_trade(trade=trade_id, session=session)
    return None


@router.put('/trade/{trade_id}/buy', status_code=status.HTTP_202_ACCEPTED, response_model=TradeBase)
async def put_trade_buy(request: Request, trade_id: int, session: Session = Depends(db.session)):
    buyer = get_profile_by_user(user=request.user.id, session=session)

    if isinstance(request.user, UnauthenticatedUser):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

    if not is_trade_exist(trade=trade_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Trade does not exist')

    # if is_seller(trade=trade_id, buyer=buyer.id, session=session):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Can not buy own item')

    trade = buy_trade_item(trade=trade_id, buyer=buyer.id, session=session)
    modify_inventory(owner=trade.seller, item=trade.item, buyer=buyer.id, session=session)
    remove_exhibition(exhibition=get_exhibition_by_trade(trade_id, session=session).id, session=session)
    return trade


@router.put('/trade/{trade_id}/extend', status_code=status.HTTP_202_ACCEPTED, response_model=TradeBase)
async def put_trade_extend(trade_id: int, session: Session = Depends(db.session)):
    if not is_trade_exist(trade=trade_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Trade does not exist')

    trade = extend_trade_expire(trade=trade_id, session=session)
    return trade


@router.put('/trade/{trade_id}/price', status_code=status.HTTP_202_ACCEPTED, response_model=TradeBase)
async def put_trade_extend(trade_id: int, info: TradePriceChange, session: Session = Depends(db.session)):
    if not is_trade_exist(trade=trade_id, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Trade does not exist')

    trade = change_trade_price(trade=trade_id, price=info.price, session=session)
    return trade


@router.get('/trades', status_code=status.HTTP_200_OK, response_model=TradesBase)
async def get_trades(request: Request, session: Session = Depends(db.session)):
    is_exhibit = request.query_params.get('is_exhibit', False)
    trades = get_trade_list(is_exhibit=is_exhibit, session=session)
    return {
        'histories': trades
    }
