#!/usr/bin/env python3
"""utility functions for token based session management"""

from os import getenv
import bcrypt
from dotenv import load_dotenv
import jwt

load_dotenv()

JWT_SECRET = getenv('JWT_SECRET')


def get_token(payload):
    claim = jwt.encode(
        payload=payload,
        key=JWT_SECRET,
        algorithm="HS256"
    )
    return claim


def verify_token(token):
    try:
        payload = jwt.decode(jwt=token,
                             key=JWT_SECRET,
                             algorithms=["HS256"]
                             )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    return payload
