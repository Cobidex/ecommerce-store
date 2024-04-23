#!/usr/bin/env python3
import functools
import jwt
from flask import request, jsonify
from lib.utils import verify_token


def admin_only(route):
    @functools.wraps(route)
    def wrapped_route(**kwargs):
        token = request.cookies.get('auth_token')
        if not token:
            return jsonify({"Error": "Unauthorized, login required!"}), 401

        user = verify_token(token)
        if not user:
            return jsonify({"Error": "Unauthorized, login"}), 401
        if not user.get('is_active'):
            return jsonify({"Error": "unauthorized, account inactive"}), 403
        if not user.get('is_admin'):
            return jsonify({"Error": "unauthorized"}), 403

        return route(**kwargs)

    return wrapped_route
