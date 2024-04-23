#!/usr/bin/env python3

"""module for buyer routes"""
from datetime import datetime, timedelta
from flask import jsonify, request, redirect, make_response
from routes import buyer_routes
from models import storage
from models.buyer import Buyer
from lib.utils import get_token, verify_token
from middlewares.auth_middleware import login_required
from middlewares.admin_middleware import admin_only
from services.redis import redisClient
from services.logger import get_logger
from services.email import email_sender


@buyer_routes.post('/buyers/register')
def register():
    form = request.get_json()

    if (form):
        buyer_data = {}
        buyer_data['email'] = form.get('email')
        buyer_data['password'] = form.get('password')
        buyer_data['first_name'] = form.get('first_name')
        buyer_data['lastname'] = form.get('last_name')
        buyer_data['is_male'] = form.get('is_male')
        buyer_data['photo_url'] = form.get('photo_url')
        buyer_data['location'] = form.get('location')
        if not buyer_data.get('email'):
            return jsonify({"Error": "missing email"}), 400
        if not buyer_data.get('password'):
            return jsonify({"Error": "missing password"}), 400

        exists = storage.get_by_email(Buyer, buyer_data.get('email'))
        if (exists):
            return jsonify({"Error": "buyer already exists"}), 409

        new_buyer = Buyer(**buyer_data)
        new_buyer.hash_password()
        new_buyer.save()

        cart_details = {"buyer_id": new_buyer.id}
        register_logger = get_logger('register_logger')
        register_logger.info(f"buyer: {new_buyer.id}, status: success")

        return jsonify(new_buyer.to_dict()), 201

    return jsonify({"Error": "not a valid json"}), 400


@buyer_routes.post('/buyers/login')
def login():
    credentials = request.get_json()
    login_logger = get_logger('buyer_login')

    if credentials:
        email = credentials.get('email')
        password = credentials.get('password')

        if not email:
            return jsonify({"Error": "missing email"}), 400
        if not password:
            return jsonify({"Error": "missing password"}), 400
        exists = storage.get_by_email(Buyer, email)
        if not exists:
            return jsonify({"Error": "User not found"}), 404
        if not exists.compare_pwd(password):
            login_logger.info(
                f"buyer: {exists.id}, status: failed, reason: incorrect password")
            return jsonify({"Error": "Unauthorized"}), 401

        td = datetime.now() + timedelta(seconds=86400)

        # auth token for session management, expires in 24hrs
        token = get_token({
            "id": exists.id,
            "model": 'Buyer',
            "is_admin": exists.is_admin,
            "is_active": exists.is_active,
            "role": 'buyer',
            "exp": td
        })

        login_logger.info(f"buyer: {exists.id}, status: success")
        response = make_response(jsonify(exists.to_dict()))
        response.set_cookie('auth_token', token, expires=td,
                            httponly=True, secure=True)
        return response

    return jsonify({"Error": "not a valid json"}), 400


@buyer_routes.get('/buyers/logout')
@login_required
def logout():
    token = get_token({"exp": 1})
    response = make_response(redirect('/login'))
    response.set_cookie('auth_token', token)
    logout_logger = get_logger('logout_user')
    logout_logger(f"buyer: {buyer.id}, status: success")
    return response


@buyer_routes.get('/buyers')
@admin_only
def GET_all_buyers():
    get_all_buyers_logger = get_logger('get_all_buyers')
    page_number = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page_number - 1) * per_page
    querry = {"offset": offset, "per_page": per_page}
    buyers = [buyer.to_dict()
              for buyer in storage.all(Buyer, **querry).values()]
    get_all_buyers_logger.info("status: success")
    return jsonify(buyers)


@buyer_routes.get('/buyers/<buyer_id>')
@admin_only
def GET_buyer(buyer_id):
    buyer = storage.get(Buyer, buyer_id)
    get_profile_logger = get_logger('get_buyer_profile')

    if (buyer):
        get_profile_logger(f"buyer: {buyer.id}, status: success")
        return jsonify(buyer.to_dict()), 200

    return jsonify({"Error": "Not found"}), 404


@buyer_routes.get('/buyers/me')
@login_required
def GET_me(user=None):
    buyer_id = user.get('id')
    get_profile_logger = get_logger('get_user_profile')

    buyer = storage.get(Buyer, buyer_id)

    if (buyer):
        get_profile_logger(f"buyer: {buyer.id}, status: success")
        return jsonify(buyer.to_dict()), 200

    return jsonify({"Error": "Not found"}), 404


@buyer_routes.patch('/buyers/me')
@login_required
def UPDATE_me(user):
    fields = request.get_json()
    update_profile_logger = get_logger('update_user_profile')

    if not fields:
        return jsonify({"Error": "Not a valid json"})

    buyer_id = user.get('id')

    password = fields.get('password')
    first_name = fields.get('first_name')
    last_name = fields.get('last_name')
    is_male = fields.get('is_male', False)
    photo_url = fields.get('photo_url')
    location = fields.get('location')

    if not (password and first_name and last_name and photo_url and location):
        return jsonify({"Error": "missing fields"}), 400

    if fields.get('email'):
        return jsonify({"Error": "use authorized route for email change"}), 403

    buyer = storage.get(Buyer, buyer_id)

    if buyer:
        buyer_data = {}
        buyer_data['password'] = password
        buyer_data['first_name'] = first_name
        buyer_data['lastname'] = last_name
        buyer_data['is_male'] = is_male
        buyer_data['photo_url'] = photo_url
        buyer_data['location'] = location
        for key, value in buyer_data.items():
            setattr(buyer, key, value)

        buyer.hash_password()
        buyer.save()
        update_profile_logger.info(f"buyer: {buyer.id}, status: success")
        return jsonify(buyer.to_dict())

    return jsonify({"Error": "Not found"}), 404


@buyer_routes.get('/buyers/request_email_verification')
@login_required
def request_email_verification(user):
    request_verification_logger = get_logger('request_user_verification')
    field = request.get_json()
    if not field:
        return jsonify({"Error": "Not a valid json"}), 400

    buyer_id = user.get('id')
    buyer = storage.get(Buyer, buyer_id)
    if not buyer:
        return jsonify({"Errro": "buyer not found"}), 404
    if buyer.email_verified:
        return jsonify({"Error": "email already verified"})

    try:
        email_sender.send_verification_code(buyer)
        request_verification_logger.info(f"buyer: {buyer.id}, status: success")
        return jsonify({"status": "email verification sent"}), 200

    except Exception as e:
        request_verification_logger.error(
            f"buyer: {buyer.id}, status: failed, reason: {str(e)}")
        return jsonify(
            {"Error": "Sorry a system error occured, try again"}), 500


@buyer_routes.patch('/buyers/update_email')
@login_required
def update_email(user):
    field = request.get_json()
    email_update_logger = get_logger('user_email_update')

    if not field:
        return jsonify({"Error": "not a valid json"})

    email = field.get('email')
    buyer_id = user.get('id')
    buyer = storage.get(Buyer, buyer_id)

    if not buyer:
        return jsonify({"Error": "buyer not found"}), 404

    buyer.email = email
    buyer.email_verified = False
    buyer.save()

    try:
        email_sender.send_verification_code(buyer)
        email_update_logger.info(f"buyer: {buyer.id}, status: success")
        return jsonify({"status": "verification email sent"}), 200

    except Exception as e:
        email_update_logger.error(
            f"buyer: {buyer.id}, status: failed, reason: {str(e)}")
        return jsonify(
            {"Error": "sorry, a system error occured, try again"}), 500


@buyer_routes.patch('/buyers/<buyer_id>/verify_email')
@admin_only
def verify_email(buyer_id):
    field = request.get_json()
    verify_email_logger = get_logger('verify_user_email')

    if not field:
        return jsonify({"Error": "not a valid json"}), 400

    buyer = storage.get(Buyer, buyer_id)
    if not buyer:
        return jsonify({"Error": "buyer not found"}), 404

    if buyer.verified:
        return jsonify({"Error": "buyer already verified"}), 403

    candidate_code = str(field.get('confirmation_code'))
    confirmation_code = redisClient.get(buyer.id)
    if not confirmation_code:
        return jsonify({"Error": "Invalid code"}), 401

    if confirmation_code != candidate_code:
        verify_email_logger.info(
            f"buyer: {buyer.id}, status: failed, reason: code mismatch")
        return jsonify({"Error": "wrong code"}), 401

    buyer.email_verified = True
    buyer.save()
    verify_email_logger.info(f"buyer: {buyer.id}, status: success")
    return jsonify(buyer.to_dict())


@buyer_routes.patch('/buyers/<buyer_id>/activate')
@admin_only
def activate_buyer(buyer_id):
    buyer = storage.get(Buyer, buyer_id)
    account_activation_logger = get_logger('account_activation')
    verification_complete_email_logger = get_logger(
        'verification_complete_email')

    if not buyer:
        return jsonify({"Error": "buyer not found"}), 404
    if not buyer.email:
        return jsonify({"Error": "profile incomplete: email is missing"}), 400
    if not buyer.password:
        return jsonify(
            {"Error": "profile incomplete: password is missing"}), 400
    if not buyer.first_name:
        return jsonify(
            {"Error": "profile incomplete: first_name is missing"}), 400
    if not buyer.last_name:
        return jsonify(
            {"Error": "profile incomplete: last_name is missing"}), 400
    if not buyer.photo_url:
        return jsonify(
            {"Error": "profile incomplete: photo_url is missing"}), 400
    if not buyer.location:
        return jsonify(
            {"Error": "profile incomplete: location is missing"}), 400
    if not buyer.email_verified:
        return jsonify(
            {"Error": "profile incomplete: email not verified"}), 400

    buyer.profile_complete = True
    buyer.save()
    account_activation_logger.info(f"buyer: {buyer.id}, status: success")

    try:
        email_sender.send_account_activation_notice(buyer)
        verification_complete_email_logger.info(
            f"buyer: {buyer.id}, status: success")

    except Exception as e:
        verification_complete_email_logger.error(
            f"buyer: {buyer.id}, status: failed, reason: {str(e)}")

    return jsonify(buyer.to_dict()), 200


@buyer_routes.patch('/buyers/activate_account')
@login_required
def activate_me(user):
    buyer_id = user.get('id')
    buyer = storage.get(Buyer, buyer_id)
    account_activation_logger = get_logger('account_activation')
    if not buyer:
        return jsonify({"Error": "buyer not found"}), 404
    if not buyer.email:
        return jsonify({"Error": "profile incomplete: email is missing"}), 400
    if not buyer.password:
        return jsonify(
            {"Error": "profile incomplete: password is missing"}), 400
    if not buyer.first_name:
        return jsonify(
            {"Error": "profile incomplete: first_name is missing"}), 400
    if not buyer.last_name:
        return jsonify(
            {"Error": "profile incomplete: last_name is missing"}), 400
    if not buyer.photo_url:
        return jsonify(
            {"Error": "profile incomplete: photo_url is missing"}), 400
    if not buyer.location:
        return jsonify(
            {"Error": "profile incomplete: location is missing"}), 400
    if not buyer.verified:
        return jsonify(
            {"Error": "profile incomplete: email not verified"}), 400

    buyer.is_active = True
    buyer.save()
    account_activation_logger.info(f"buyer: {buyer.id}, status: success")

    try:
        email_sender.send_account_activation_notice(buyer)
        account_activation_logger.info(f"buyer: {buyer.id}, status: success")

    except Exception as e:
        account_activation_logger.error(
            f"buyer: {buyer.id}, status: failed, reason: {str(e)}")

    return jsonify(buyer.to_dict()), 200


@buyer_routes.delete('/buyers/<buyer_id>/deactivate_account')
@admin_only
def deactivate_buyer(buyer_id):
    token = request.cookies.get('auth_token')
    user = verify_token(token)
    account_deactivation_logger = get_logger('account_deactivation')

    buyer = storage.get(Buyer, buyer_id)
    if buyer:
        buyer['is_active'] = False
        buyer.save()
        return jsonify({"Status": "success"}), 200
    account_deactivation_logger.info(f"buyer: {buyer.id}, status: success")
    return jsonify({"Error": "Not found"}), 404


@buyer_routes.delete('/buyers/deactivate_account')
@login_required
def deactivate_me(user):
    buyer_id = user.get('id')
    account_deactivation_logger = get_logger('account_deactivation')

    buyer = storage.get(Buyer, buyer_id)
    if buyer:
        buyer['is_active'] = False
        buyer.save()
        account_deactivation_logger.info(f"buyer: {buyer.id}, status: success")
        return jsonify({"Status": "success"}), 200
    return jsonify({"Error": "Not found"}), 404
