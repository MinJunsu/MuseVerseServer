from fastapi import APIRouter, status, Depends

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.models import OrderRegister, Order
from app.database.schema import Orders, Inventories, Profiles, Trades, Items, db


router = APIRouter()


@router.post('/order', status_code=status.HTTP_201_CREATED, response_model=Order)
async def order_item(request: Request, info: OrderRegister, session: Session = Depends(db.session)):
    buyer = Profiles.get(user=request.user.id).id

    # * Already Exist Order
    if is_order_exists(buyer_id=buyer, item_id=info.item, trade_id=info.trade):
        Exception()

    # * Order item not equal Error
    if not await is_owner(buyer, info.item):
        Exception()

    order = Orders.create(session=session, auto_commit=True, buyer=buyer, item=info.item,
                          trade=info.trade, price=Items.get(id=info.item).price, status=info.status)

    # TODO: 아이템의 소유권 이전
    Inventories.get(owner=Trades.get(id=info.trade).owner, item=info.item).delete()
    Inventories.create(session=session, auto_commit=True, owner=buyer, item=info.item)

    return order


@router.delete('/order/{order_id}', status_code=status.HTTP_202_ACCEPTED)
async def delete_order(request: Request, order_id: int):
    buyer = Profiles.get(user=request.user.id).id
    order = Orders.get(id=order_id)

    # * Seller Buyer equal Error
    if not await is_buyer(buyer, order_id):
        Exception()

    # * Order not exists Error
    if not order:
        raise Exception()

    order.delete()

    return None


@router.get('/orders', status_code=status.HTTP_201_CREATED, response_model=list[Order])
async def get_recent_orders():
    orders = Orders.order_by('-created_at')[:50]
    return orders


@router.get('/orders/{trade_id}', status_code=status.HTTP_200_OK, response_model=list[Order])
async def get_trade_orders(trade_id: int):
    # * Trade does not exists Error
    if not Trades.get(id=trade_id):
        raise Exception()
    return Orders.filter(trade=trade_id).all()


async def is_order_exists(buyer_id: int, item_id: int, trade_id: int):
    if Orders.get(buyer=buyer_id, item=item_id, trade=trade_id):
        return True
    return False


async def is_buyer(buyer_id: int, order_id: int):
    if Orders.get(id=order_id).buyer == buyer_id:
        return True
    return False


async def is_owner(buyer_id: int, item_id):
    if Inventories.get(item=item_id).owner == buyer_id:
        return True
    return False
