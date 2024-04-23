from datetime import datetime, timedelta
from flask import request, jsonify
from routes import cart_routes
from middlewares.buyer_middleware import buyers_only
from models import storage
from models.cart import Cart
from models.product import Product


@cart_routes.get('/carts')
@buyers_only
def get_cart_items(user):
    cart = Cart(request, user)
    cart_items = cart.get_cart(user)
    return jsonify(cart_items), 200


@cart_routes.post('/carts/add-to-cart')
@buyers_only
def add_to_cart(user):
    fields = request.get_json()
    if not fields:
        return jsonify({"Error": "not a valid json"}), 400
    product_id = fields.get('product_id')
    qty = fields.get('qty')
    location_id = fields.get('location_id')

    product = storage.get(Product, product_id)
    if not product:
        return jsonify({"Error": "product not found"}), 404
    if product.in_stock <= 0:
        return jsonify({"Error": "Product out of stock"}), 403
    if not location_id:
        return jsonify({"Error": "location_id missing"}), 404

    for location in product.delivery_locations:
        if location_id == location.id:
            cost_of_delivery = location.cost_of_delivery
            cart = Cart(request, user)
            cart_items = cart.add(product, qty, cost_of_delivery, user)
            return jsonify(cart_items), 200
    return jsonify({"Error": "location not available for this product"}), 400


@cart_routes.delete('/carts/<product_id>')
@buyers_only
def remove_from_cart(user, product_id):
    cart = Cart(request, user)
    cart_items = cart.remove(product_id, user)
    return jsonify(cart_items), 200
