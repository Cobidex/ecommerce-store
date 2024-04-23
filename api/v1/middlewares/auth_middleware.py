#!/usr/bin/env python3
import functools
import jwt
from flask import request, jsonify
from lib.utils import verify_token


def login_required(route):
    @functools.wraps(route)
    def wrapped_route(**kwargs):
        token = request.cookies.get('auth_token')
        if not token:
            return jsonify({"Error": "Unauthorized, login required!"}), 401

        user = verify_token(token)
        if not user:
            return jsonify({"Error": "unauthorized, log in"}), 401
        if not user.get('is_active'):
            return jsonify(
                {"Error": "unauthorized, account not yet active"}), 403

        return route(user, **kwargs)

    return wrapped_route
