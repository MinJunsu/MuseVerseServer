from fastapi import Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.database.conn import db
from app.database.schema import Users, Profiles

from app.models.auth import AuthUserCreate


def is_username_exist(username: str, session: Session) -> bool:
    session = next(db.session())
    return session.query(session.query(Users).filter(Users.username == username).exists()).scalar()


def is_profile_exist(user: int, session: Session) -> bool:
    session = next(db.session())
    return session.query(session.query(Profiles).filter(Profiles.user == user).exists()).scalar()


def get_user_by_username(username: str, session: Session) -> Users:
    session = next(db.session())
    query = session.query(Users).filter(Users.username == username)
    return query.one()


def get_user_by_id(user_id: int, session: Session) -> Users:
    session = next(db.session())
    query = session.query(Users).filter(Users.id == user_id)
    return query.one()


def get_profile_by_user(user: int, session: Session) -> Profiles:
    session = next(db.session())
    query = session.query(Profiles).filter(Profiles.user == user)
    return query.one()


def get_profile_by_id(profile: int, session: Session) -> Profiles:
    session = next(db.session())
    query = session.query(Profiles).filter(Profiles.id == profile)
    return query.one()


def get_profile_nickname_by_id(profile: int, session: Session) -> str | None:
    session = next(db.session())
    if profile is None:
        return None
    query = session.query(Profiles).filter(Profiles.id == profile).one()
    return query.nickname


def create_user(info: AuthUserCreate, session: Session) -> Users:
    session = next(db.session())
    if is_username_exist(username=info.username, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exist')
    user = Users(username=info.username, password=info.password, email=info.email)
    session.add(user)
    session.commit()
    return user


def create_profile(user: int, nickname: str, session: Session) -> Profiles:
    session = next(db.session())
    if is_profile_exist(user=user, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User Profile already exist')
    profile = Profiles(user=user, nickname=nickname, money=0)
    session.add(profile)
    session.commit()
    return profile


def modify_profile_nickname(profile: int, nickname: str, session: Session) -> Profiles:
    session = next(db.session())
    query = session.query(Profiles).filter(Profiles.id == profile)
    query.update({'nickname': nickname})
    session.commit()
    return query.one()
