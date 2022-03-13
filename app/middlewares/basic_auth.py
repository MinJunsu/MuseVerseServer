import logging

import jwt
import binascii

from fastapi import Depends

from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser
)
from jwt.exceptions import ExpiredSignatureError, DecodeError

from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.conn import db
from app.queries.auth import get_user_by_username


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != 'bearer':
                return
            decoded = await token_decode(credentials)
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise AuthenticationError('Invalid basic auth credentials')

        username = decoded.get('username')

        return AuthCredentials(["authenticated"]), get_user_by_username(username=username, session=next(db.session()))


async def token_decode(access_token):
    """
    :param access_token:
    :return:
    """
    try:
        payload = jwt.decode(access_token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError as e:
        print(e)
    except DecodeError as e:
        print(e)
    return payload
