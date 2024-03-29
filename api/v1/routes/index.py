#!/usr/bin/env python3
"""non-specific endpoints"""
from datetime import datetime, timedelta
from flask import make_response, redirect
from routes import app_routes
from middlewares.auth_middleware import login_required
from lib.utils import get_token


@app_routes.get('/logout')
@login_required
def logout():
    td = datetime.utcnow()+timedelta(seconds=86400)
    token = get_token({"exp": 1})
    response = make_response(redirect('/login'))
    response.set_cookie('auth_token', token, expires=td,\
                         httponly=True, secure=True)
    return response