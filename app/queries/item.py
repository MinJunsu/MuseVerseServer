from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.schema import Items, Inventories, db


def is_item_owner(owner: int, item: int, session: Session) -> bool:
    session = next(db.session())
    return session.query(Inventories).filter(Inventories.item == item,
                                             Inventories.is_deleted == False).one().owner == owner


def is_item_exists(item: int, session: Session) -> bool:
    session = next(db.session())
    return session.query(session.query(Items).filter(Items.id == item, Items.is_deleted == False).exists()).scalar()


def create_item(name: str, author: int, upload: str, file_format: str, session: Session) -> Items:
    session = next(db.session())
    item = Items(name=name, author=author, upload=upload, file_format=file_format)
    session.add(item)
    session.commit()
    return item


def create_inventory(owner: int, item: int, session: Session) -> Inventories:
    session = next(db.session())
    inventory = Inventories(owner=owner, item=item)
    session.add(inventory)
    session.commit()
    return inventory


def get_user_inventories(profile: int, session: Session) -> list[Items]:
    session = next(db.session())
    return session.query(Items).join(Inventories, Inventories.owner == profile).filter(Items.is_deleted == False).all()


def get_item_by_id(item: int, session: Session) -> Items:
    session = next(db.session())
    query = session.query(Items).filter(Items.id == item, Items.is_deleted == False)
    return query.one()


def modify_inventory(owner: int, item: int, buyer: int, session: Session) -> Inventories:
    session = next(db.session())
    query = session.query(Inventories).filter(Inventories.item == item, Inventories.owner == owner)
    query.update({'owner': buyer})
    session.commit()
    return query.one()


def remove_item(item: int, session: Session) -> Items:
    session = next(db.session())
    inventory = session.query(Inventories).filter(Inventories.item == item)
    inventory.delete()

    query = session.query(Items).filter(Items.id == item)
    query.update({'is_deleted': True})

    session.commit()
    return query
