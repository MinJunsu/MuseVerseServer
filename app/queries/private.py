from sqlalchemy.orm import Session

from app.database.schema import PrivateRooms, db
from app.models.private import PrivateExhibitionCreate


def is_num_exists(num: int, owner: int, session: Session):
    session = next(db.session())
    return session.query(session.query(PrivateRooms).filter(
        PrivateRooms.num == num, PrivateRooms.owner == owner, PrivateRooms.is_deleted == False).exists()).scalar()


def is_private_owner(private: int, owner: int, session: Session):
    session = next(db.session())
    return session.query(session.query(PrivateRooms).filter(
        PrivateRooms.id == private, PrivateRooms.owner == owner, PrivateRooms.is_deleted == False).exists()).scalar()


def is_private_exists(private: int, session: Session):
    session = next(db.session())
    return session.query(session.query(PrivateRooms).filter(
        PrivateRooms.id == private, PrivateRooms.is_deleted == False).exists()).scalar()


def create_private_exhibition(info: PrivateExhibitionCreate, owner: int, session: Session) -> PrivateRooms:
    session = next(db.session())
    private_room = PrivateRooms(owner=owner, item=info.item, num=info.num)
    session.add(private_room)
    session.commit()
    return private_room


def get_private_exhibition(private: int, session: Session) -> PrivateRooms:
    session = next(db.session())
    query = session.query(PrivateRooms).filter(PrivateRooms.id == private)
    return query.one()


def remove_private_exhibition(private: int, session: Session) -> PrivateRooms:
    session = next(db.session())
    query = session.query(PrivateRooms).filter(PrivateRooms.id == private)
    query.update({'is_deleted': True})
    session.commit()
    return query
