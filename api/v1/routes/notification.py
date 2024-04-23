#!/usr/bin/env python3

"""module for notification routes"""
from flask import jsonify, request
from routes import notification_routes
from models import storage
from models.notification import Notification


@notification_routes.get('/notifications')
def GET_all_notifications():
    page_number = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page_number - 1) * per_page
    querry = {"offset": offset, "per_page": per_page}
    notifications = [notification.to_dict() for notification in storage.all(
        Notification, **querry).values()]
    return jsonify(notifications)


@notification_routes.get('/notifications/<notification_id>')
def GET_notification(notification_id):
    notification = storage.get(Notification, notification_id)
    if (notification):
        return jsonify(notification.to_dict()), 200
    return jsonify({"Error": "Not found"}), 404
