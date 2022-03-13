from datetime import timedelta

from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.conn import db
from app.database.schema import Exhibitions
from app.models.exhibition import ExhibitionCreate


def is_item_exhibit(item: int, session: Session) -> bool:
    session = next(db.session())
    return session.query(session.query(Exhibitions).filter(Exhibitions.item == item,
                                                           Exhibitions.is_deleted == False).exists()).scalar()


def is_number_exists(hall: int, num: int, session: Session) -> bool:
    session = next(db.session())
    return session.query(session.query(Exhibitions).filter(
        Exhibitions.hall == hall, Exhibitions.num == num, Exhibitions.is_deleted == False).exists()).scalar()


def is_exhibition_exists(exhibition: int, session: Session) -> bool:
    session = next(db.session())
    return session.query(session.query(Exhibitions).filter(Exhibitions.id == exhibition
                                                           , Exhibitions.is_deleted == False).exists()).scalar()


def is_exhibition_owner(exhibition: int, owner: int, session: Session) -> bool:
    session = next(db.session())
    return session.query(Exhibitions).filter(Exhibitions.id == exhibition,
                                             Exhibitions.is_deleted == False).one().owner == owner


def create_exhibition(info: ExhibitionCreate, owner: int, trade: int,
                      session: Session) -> Exhibitions:
    session = next(db.session())
    exhibition = Exhibitions(item=info.item, owner=owner, trade=trade, hall=info.hall, num=info.num)
    session.add(exhibition)
    session.commit()
    return exhibition


def get_exhibition_by_hall_num(hall: int, num: int, session: Session) -> Exhibitions:
    session = next(db.session())
    query = session.query(Exhibitions).filter(Exhibitions.hall == hall, Exhibitions.num == num,
                                              Exhibitions.is_deleted == False)
    return query.one()


def get_exhibition_by_trade(trade_id: int, session: Session) -> Exhibitions:
    session = next(db.session())
    query = session.query(Exhibitions).filter(Exhibitions.trade == trade_id, Exhibitions.is_deleted == False)
    return query.one()


def get_user_exhibitions(profile: int, session: Session) -> list[Exhibitions]:
    session = next(db.session())
    return session.query(Exhibitions).filter(Exhibitions.owner == profile, Exhibitions.is_deleted == False).all()


def modify_exhibition_expire(exhibition: int, session: Session) -> Exhibitions:
    session = next(db.session())
    query = session.query(Exhibitions).filter(Exhibitions.id == exhibition)
    query.update({'expire': query.one().expire + timedelta(days=14)})
    session.commit()
    return query.one()


def remove_exhibition(exhibition: int, session: Session) -> Exhibitions:
    session = next(db.session())
    query = session.query(Exhibitions).filter(Exhibitions.id == exhibition)
    query.update({'is_deleted': True})
    session.commit()
    return query.one()
