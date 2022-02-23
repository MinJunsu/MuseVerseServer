from fastapi import APIRouter, status, Depends

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.models import OrderRegister, Order
from app.database.conn import db
from app.database.schema import Orders, Inventories, Profiles, Trades


router = APIRouter()


@router.post('/order', status_code=status.HTTP_201_CREATED, response_model=Order)
async def order_item(request: Request, info: OrderRegister, session: Session = Depends(db.session)):
    buyer = Profiles.get(user=request.user.id).id

    # * Order item not equal Error
    if not await is_owner(buyer, info.item):
        Exception()

    # * Order price under zero Error
    if info.price < 0:
        Exception()

    order = Orders.create(session=session, auto_commit=True, buyer=buyer, item=info.item,
                          trade=info.trade, price=info.price, status=info.status)
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


async def is_buyer(buyer_id: int, order_id: int):
    if Orders.get(id=order_id).buyer == buyer_id:
        return True
    return False


async def is_owner(buyer_id: int, item_id):
    if Inventories.get(item=item_id).owner == buyer_id:
        return True
    return False
