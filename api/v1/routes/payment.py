import hashlib
import hmac
import json
from os import getenv
from flask import jsonify, request
from routes import payement_routes
from models.order import Order, OrderItem
from models.buyer import Buyer
from models import storage
from services.email import email_sender


@payement_routes.post("/payments/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    hash_algorithm = hashlib.sha512()
    hash_algorithm.update(json.dumps(body).encode())
    hash_signature = hmac.new(getenv('PAYMENT_SECRET_KEY').encode(),
                              hash_algorithm.digest(),
                              hashlib.sha512).hexdigest()

    if hash_signature == request.headers.get("X-Paystack-Signature"):
        if body.get('event') == 'paymentrequest.success':
            data = body.get('data')
            meta_data = data.get('metadata')
            order_id = meta_data.get('order_id')
            order = storage.get(Order, order_id)
            order.billing_status = True
            order.amount_paid = data.get('amount')
            buyer = storage.get(Buyer, order.buyer_id)
            info = {
                "email": buyer.email,
                "amount": order.amount_paid,
                "order_id": order.id
            }
            email_sender.send_receipt_to_buyer(**info)

            items = storage.get_order_item(OrderItem, order.id)
            for item in items:
                info = {
                    "vendor_email": item.vendor_email,
                    "id": item.id
                }
                email_sender.notify_vendor(**info)

            return jsonify({"status": "success"}), 200
    else:
        return jsonify({"error": "Invalid signature"}), 400
