#!/usr/bin/env python3

"""module for user routes"""
from datetime import datetime, timedelta
from flask import jsonify, request, redirect, make_response
from routes import vendor_routes
from models import storage
from models.vendor import Vendor
from models.notification import Notification
from lib.utils import get_token, verify_token
from middlewares.vendor_middleware import vendors_only
from middlewares.auth_middleware import login_required
from middlewares.admin_middleware import admin_only
from services.email import email_sender
from services.logger import get_logger


@vendor_routes.post('/vendors/register')
def register():
    form = request.get_json()

    if (form):
        vendor_data = {}
        vendor_data['email'] = form.get('email')
        vendor_data['password'] = form.get('password')
        vendor_data['first_name'] = form.get('first_name')
        vendor_data['lastname'] = form.get('last_name')
        vendor_data['is_male'] = form.get('is_male')
        vendor_data['photo_url'] = form.get('photo_url')
        vendor_data['location'] = form.get('location')
        vendor_data['department'] = form.get('department')
        vendor_data['level'] = form.get('level')
        vendor_data['reg_number'] = form.get('reg_number')
        if not vendor_data.get('email'):
            return jsonify({"Error": "missing email"}), 400
        if not vendor_data.get('password'):
            return jsonify({"Error": "missing password"}), 400

        exists = storage.get_by_email(Vendor, vendor_data.get('email'))
        if (exists):
            return jsonify({"Error": "Vendor already exists"}), 409

        new_vendor = Vendor(**vendor_data)
        new_vendor.hash_password()
        new_vendor.save()
        register_logger = get_logger('register_vendor')
        register_logger.info(f"vendor: {new_vendor.id}, status: success")

        return jsonify(new_vendor.to_dict()), 201

    return jsonify({"Error": "not a valid json"}), 400


@vendor_routes.get('/vendors/request_approval')
@vendors_only
def request_approval():
    token = request.cookies.get('auth_token')
    user = verify_token(token)
    vendor_id = user.get('id')
    admin_notification_logger = get_logger('admin_notification')

    note = {"vendor_id": vendor_id}
    notice = Notification(**note)
    notice.save()
    try:
        print('here now')
        email_sender.notify_admin_for_approval(vendor_id)
        admin_notification_logger.info(f"vendor: {vendor_id}, status: success")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        admin_notification_logger.error(
            f"vendor: {vendor_id}, status: failed, reason: {str(e)}")
        return jsonify({"Error": "sorry something went wrong, try again"}), 500


@vendor_routes.post('/vendors/login')
def login():
    credentials = request.get_json()
    login_logger = get_logger('login_vendor')

    if credentials:
        email = credentials.get('email')
        password = credentials.get('password')

        if not email:
            return jsonify({"Error": "missing email"}), 400
        if not password:
            return jsonify({"Error": "missing password"}), 400
        exists = storage.get_by_email(Vendor, email)
        if not exists:
            return jsonify({"Error": "User not found"}), 404
        if not exists.compare_pwd(password):
            login_logger.info(
                f"vendor: {exists.id}, status: failed, reason: incorrect password")
            return jsonify({"Error": "Unauthorized"}), 401

        td = datetime.now() + timedelta(seconds=86400)

        # auth token for session management, expires in 24hrs
        token = get_token({
            "id": exists.id,
            "verified": exists.email_verified,
            "is_admin": exists.is_admin,
            "is_active": exists.is_active,
            "role": 'vendor',
            "exp": td
        })

        login_logger.info(f"vendor: {exists.id}, status: success")
        response = make_response(jsonify(exists.to_dict()))
        response.set_cookie('auth_token', token, expires=td,
                            httponly=True, secure=True)
        return response

    return jsonify({"Error": "not a valid json"}), 400


@vendor_routes.get('/vendors')
@admin_only
def GET_all_vendors():
    vendors = [vendor.to_dict() for vendor in storage.all(Vendor).values()]
    get_all_vendors_logger = get_logger('get_all_vendors')
    get_all_vendors_logger.info("status: success")
    return jsonify(vendors), 200


@vendor_routes.get('/vendors/<vendor_id>')
@login_required
def GET_vendor(vendor_id):
    vendor = storage.get(Vendor, vendor_id)
    if (vendor):
        get_profile_logger = get_logger('get_vendor_profile')
        get_profile_logger(f"vendor: {vendor.id}, status: success")
        return jsonify(vendor.to_dict()), 200
    return jsonify({"Error": "Not found"}), 404


@vendor_routes.get('/vendors/me')
@vendors_only
def GET_me(user=None):
    vendor_id = user.get('id')

    vendor = storage.get(vendor, vendor_id)

    if (vendor):
        get_profile_logger = get_logger('get_vendor_profile')
        get_profile_logger(f"vendor: {vendor.id}, status: success")
        return jsonify(vendor.to_dict()), 200

    return jsonify({"Error": "Not found"}), 404


@vendor_routes.patch('/vendors/update_profile')
@vendors_only
def UPDATE_me(user):
    fields = request.get_json()
    if not fields:
        return jsonify({"Error": "Not a valid json"})

    vendor_id = user.get('id')
    vendor = storage.get(Vendor, vendor_id)

    if vendor:
        vendor_data = {}
        vendor_data['email'] = fields.get('email')
        vendor_data['password'] = fields.get('password')
        vendor_data['first_name'] = fields.get('first_name')
        vendor_data['lastname'] = fields.get('last_name')
        vendor_data['is_male'] = fields.get('is_male')
        vendor_data['photo_url'] = fields.get('photo_url')
        vendor_data['location'] = fields.get('location')
        vendor_data['department'] = fields.get('department')
        vendor_data['level'] = fields.get('level')
        vendor_data['reg_number'] = fields.get('reg_number')
        for key, value in fields.items():
            setattr(vendor, key, value)
        vendor.hash_password()
        vendor.save()
        update_profile_logger = get_logger('update_vendor_profile')
        update_profile_logger.info(f"vendor: {vendor.id}, status: success")
        return jsonify(vendor.to_dict()), 200

    return jsonify({"Error": "Not found"}), 404


@vendor_routes.patch('/vendors/<vendor_id>')
@admin_only
def verify_vendor(vendor_id):
    vendor = storage.get(Vendor, vendor_id)
    if vendor:
        vendor.verified = True
        vendor.save()
        return jsonify(vendor.to_dict()), 200
    return jsonify({"Error": "Not found"}), 404


@vendor_routes.delete('/vendors/deactivate_account')
@vendors_only
def deactivate_me(user):
    vendor_id = user.get('id')

    vendor = storage.get(Vendor, vendor_id)
    if vendor:
        vendor['is_active'] = False
        vendor.save()
        account_deactivation_logger = get_logger('vendor_account_deactivation')
        account_deactivation_logger.info(
            f"vendor: {vendor.id}, status: success")
        return jsonify({"Status": "success"}), 200
    return jsonify({"Error": "Not found"}), 404


@vendor_routes.delete('/vendors/<vendor_id>/deactivate_account')
@admin_only
def deactivate_vendor(vendor_id):
    token = request.cookies.get('auth_token')
    user = verify_token(token)

    vendor = storage.get(Vendor, vendor_id)
    if vendor:
        vendor['is_active'] = False
        vendor.save()
        return jsonify({"Status": "success"}), 200
    account_deactivation_logger = get_logger('vendor_account_deactivation')
    account_deactivation_logger.info(f"vendor: {vendor.id}, status: success")
    return jsonify({"Error": "Not found"}), 404


@vendor_routes.patch('/vendors/<vendor_id>/make-admin')
@admin_only
def make_admin(vendor_id):
    vendor = storage.get(Vendor, vendor_id)
    if vendor:
        vendor.is_admin = True
        vendor.save()
        admin_creation_logger = get_logger('admin_creation')
        admin_creation_logger.info(f"vendor: {vendor.id}, status: success")
        return jsonify(vendor.to_dict()), 201
    return jsonify({"Error": "Not found"}), 404
