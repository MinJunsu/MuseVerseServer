from datetime import datetime, timedelta

from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.conn import db
from app.database.schema import Items, Trades, Exhibitions
from app.models.trade import TradeCreate


def is_trade_exist(trade: int, session: Session) -> bool:
    session = next(db.session())
    return session.query(session.query(Trades).filter(Trades.id == trade, Trades.is_deleted == False).exists()).scalar()


def is_item_exist(item: int, session: Session) -> bool:
    session = next(db.session())
    return session.query(session.query(Trades).filter(Trades.item == item,
                                                      Trades.is_deleted == False).exists()).scalar()


def is_seller(trade: int, buyer: int, session: Session) -> bool:
    session = next(db.session())
    return session.query(Trades).filter(Trades.id == trade).one().seller == buyer


def create_trade(info: TradeCreate, seller: int, session: Session) -> Trades:
    session = next(db.session())
    trade = Trades(seller=seller, item=info.item, price=info.price)
    session.add(trade)
    session.commit()
    return trade


def create_or_get_trade(item: int, seller: int, price: float, session: Session) -> Trades:
    session = next(db.session())
    if session.query(session.query(Trades).filter(Trades.item == item, Trades.is_deleted == False).exists()).scalar():
        trade = session.query(Trades).filter(Trades.item == item, Trades.is_deleted == False).one()
    else:
        trade = Trades(seller=seller, item=item, price=price)
        session.add(trade)
        session.commit()
    return trade


def get_user_buy_history(profile: int, session: Session) -> list[Trades]:
    session = next(db.session())
    return session.query(Trades).filter(Trades.buyer == profile, Trades.is_deleted == False).all()


def get_user_sell_history(profile: int, session: Session) -> list[Trades]:
    session = next(db.session())
    return session.query(Trades).filter(Trades.seller == profile, Trades.is_deleted == False).all()


def get_trade_by_id(trade: int, session: Session) -> Trades:
    session = next(db.session())
    query = session.query(Trades).filter(Trades.id == trade)
    return query.one()


def get_trade_list(is_exhibit: bool, session: Session) -> list[Trades]:
    session = next(db.session())
    query = session.query(Trades).filter(Trades.expire >= datetime.now(), Trades.is_deleted == False)
    if is_exhibit:
        return query.all()
    exhibit_query = session.query(Trades).join(Exhibitions, Trades.id == Exhibitions.trade).filter(
        Trades.expire >= datetime.now(), Trades.is_deleted == False)
    return session.query().except_(exhibit_query).all()


def extend_trade_expire(trade: int, session: Session) -> Trades:
    session = next(db.session())
    query = session.query(Trades).filter(Trades.id == trade)
    query.update({'expire': query.one().expire + timedelta(days=14)})
    session.commit()
    return query.one()


def change_trade_price(trade: int, price: float, session: Session) -> Trades:
    session = next(db.session())
    query = session.query(Trades).filter(Trades.id == trade)
    query.update({'price': price})
    session.commit()
    return query.one()


def buy_trade_item(trade: int, buyer: int, session: Session) -> Trades:
    session = next(db.session())
    query = session.query(Trades).filter(Trades.id == trade)
    query.update({'buyer': buyer})
    session.commit()
    return query.one()


def remove_trade(trade: int, session: Session) -> Trades:
    session = next(db.session())
    query = session.query(Trades).filter(Trades.id == trade)
    query.update({'is_delete': True})
    session.commit()
    return query.one()
