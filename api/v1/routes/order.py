from flask import jsonify, request
from models.order import Order, OrderItem
from routes import order_routes
from middlewares.buyer_middleware import buyers_only
from middlewares.vendor_middleware import vendors_only
from services.email import email_sender
from models.cart import Cart
from models import storage

@order_routes.patch('/orders/<item_id>')
@vendors_only
def send_delivery_token(user, item_id):
    item = storage.get(OrderItem, item_id)
    if not item:
        return jsonify({"Error": "Item not found"}), 404
    if user.get('id') != item.vendor_id:
        return jsonify({"Error": "Not your product"}), 403
    order = storage.get(Order, item.order)
    email_sender.send_delivery_token(order.email, item)
    return jsonify({"status": "success"}), 200
    
@order_routes.patch('/orders/verify_delivery_code')
@vendors_only
def verify_delivery_code(user):
    fields = request.get_json()
    if not fields:
        return jsonify({"Error": "Not a valid json"}), 400
    code = fields.get('delivery_code')
    item_id = fields.get('item_id')
    if not (code and item_id):
        return jsonify({"Error": "missing field"})
    
    item = storage.get(OrderItem, item_id)
    if not item:
        return jsonify({"Error": "Item not found"}), 404
    if user.get('id') != item.vendor_id:
        return jsonify({"Error": "Not your product"}), 403
    if code != item.delivery_code:
        return jsonify({"Error": "Code is incorrect"}), 400
    item.delivered = True
    item.save()
    return jsonify(item.to_dict()), 200



@order_routes.post('/orders')
@buyers_only
def create_order(user):
    fields = request.get_json()
    if not fields:
        return jsonify({"Error": "Not a valid json"}), 400
    buyer_id = user.get('id')
    email = fields.get('email')
    full_name = fields.get('full_name')
    address = fields.get('address')
    city = fields.get('city')
    phone = fields.get('phone')
    order_key = fields.get('order_key')

    if not (full_name and buyer_id and address and city and phone and order_key and email):
        return jsonify({"Error": "field missing"}), 400
    
    cart = Cart(request, user)
    cart_content = cart.get_cart(user)
    order = {
        "buyer_id": buyer_id,
        "full_name": full_name,
        "email": email,
        "address": address,
        "city": city,
        "phone": phone,
        "order_key": order_key,
        "amount_paid": cart_content.get('grand_total')
    }
    new_order = Order(**order)
    new_order.save()

    for key, value in cart_content.items():
        if isinstance(value, dict):
            order_item = {
                "product": key,
                "vendor_id": value.get('vendor_id'),
                "order": new_order.id,
                "price": value.get('price'),
                "qty": value.get('qty')
            }

            new_order_item = OrderItem(**order_item)
            new_order_item.save()
    return jsonify(new_order.to_dict()), 201