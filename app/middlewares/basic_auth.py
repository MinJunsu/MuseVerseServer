import logging

import jwt
import binascii

from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser
)
from jwt.exceptions import ExpiredSignatureError, DecodeError

from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.schema import Users, Profiles


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

        # TODO: You'd want to verify the username and password here.
        return AuthCredentials(["authenticated"]), Users.get(username=username)


async def token_decode(access_token):
    """
    :param access_token:
    :return:
    """
    try:
        payload = jwt.decode(access_token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError as e:
        pass
    except DecodeError as e:
        pass
    return payload
