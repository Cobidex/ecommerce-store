#!/usr/bin/env python3

"""module for product routes"""
from flask import jsonify, request
from routes import product_routes
from models import storage
from models.product import Product, DeliveryLocation
from middlewares.vendor_middleware import vendors_only
from services.logger import get_logger


@product_routes.get('/products')
def GET_all_products():
    get_all_products_logger = get_logger('get_all_products')
    page_number = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page_number - 1) * per_page
    querry = {"offset": offset, "per_page": per_page}
    products = [product.to_dict()
                for product in storage.all(Product, **querry).values()]
    if len(products) <= 0:
        return jsonify({"Error": "No Product available"}), 404
    get_all_products_logger.info("status: success")
    return jsonify(products)


@product_routes.get('/products/search')
def SEARCH_products():
    search_product_logger = get_logger('search_product')
    page_number = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page_number - 1) * per_page
    name = request.args.get('name')

    querry = {"offset": offset, "per_page": per_page, "name": name}
    products = storage.search_products(Product, **querry)
    if len(products) <= 0:
        search_product_logger.info(
            f"search: {name}, status: failed, reason: not found")
        return jsonify({"Error": "No product found"}), 404

    products = [prod.to_dict() for prod in products]
    search_product_logger.info(f"search: {name}, status: success")
    return jsonify(products)


@product_routes.get('/products/<product_id>')
def GET_product(product_id):
    get_product_logger = get_logger('get_product')
    product = storage.get(Product, product_id)
    if (product):
        get_product_logger.info(f"product: {product.id}, status: success")
        return jsonify(product.to_dict()), 200
    return jsonify({"Error": "Not found"}), 404


@product_routes.patch('/products/<product_id>')
@vendors_only
def UPDATE_product(user, product_id):
    product_update_logger = get_logger('product_update')
    fields = request.get_json()

    if not fields or len(fields) == 0:
        return jsonify({"Error": "Not a valid json"})

    vendor_id = user.get('id')
    name = fields.get('name'),
    description = fields.get('description'),
    price = fields.get('price'),
    quantity = fields.get('quantity'),
    category_id = fields.get('category_id'),
    photo_urls = fields.get('photo_urls')

    if not (name and description and price and quantity and category_id and photo_urls):
        return jsonify({"Error": "missing fields"}), 400

    product_fields = {
        "name": name,
        "description": description,
        "price": price,
        "quantity": quantity,
        "category_id": category_id,
        "photo_urls": photo_urls
    }

    product = storage.get(Product, product_id)
    if not product:
        return jsonify({"Error": "Not found"}), 404

    if vendor_id != product.vendor_id:
        return jsonify({"Error": "unauthorized"}), 403

    for key, value in product_fields:
        setattr(product, key, value)

    product.save()
    product_update_logger.info(f"product: {product.id}, status: success")
    return jsonify(product.to_dict())


@product_routes.post('/products')
@vendors_only
def POST_product(user):
    fields = request.get_json()
    if not fields:
        return jsonify({"Error": "Not a valid json"})

    if 'name' not in fields:
        return jsonify({"Error": "name is missing"}), 400
    if 'category_id' not in fields:
        return jsonify({"Error": "category_id is missing"}), 400
    if 'photo_urls' not in fields:
        return jsonify({"Error": "photo_urls is missing"}), 400
    if 'category_id' not in fields:
        return jsonify({"Error": "category_id is missing"}), 400
    if 'delivery_locations' not in fields:
        return jsonify({"Error": "delivery_locations missing"}), 400

    product_fields = {
        'name': fields.get('name'),
        'description': fields.get('description'),
        'price': fields.get('price'),
        'in_stock': fields.get('in_stock'),
        'category_id': fields.get('category_id'),
        'vendor_id': user.get('id'),
        'photo_urls': fields.get('photo_urls')
    }

    upload_product_logger = get_logger('upload_product')

    urls = product_fields.get('photo_urls')
    if type(urls) != list:
        return jsonify({"Error": "photo_urls must be an array"}), 400
    if len(urls) > 3:
        return jsonify({"Error": "photo urls more than 3"}), 400

    locations = fields.get('delivery_locations')
    delivery_locations = []

    for location in locations:
        location_details = {}
        if not location.get('address'):
            return jsonify({"Error": "a location's address is missing"}), 400
        location_details['address'] = location.get('address')
        location_details['cost_of_delivery'] = int(
            location.get('cost_of_delivery'))
        new_delivery_location = DeliveryLocation(**location_details)
        delivery_locations.append(new_delivery_location)

    product_fields['delivery_locations'] = delivery_locations
    new_product = Product(**product_fields)
    new_product.save()
    upload_product_logger.info(f"product: {new_product.id}, status: success")

    return jsonify(new_product.to_dict())


@product_routes.delete('/products/<product_id>')
@vendors_only
def DELETE_product(user, product_id):
    vendor_id = user.get('id')
    product = storage.get(Product, product_id)
    delete_product_logger = get_logger('delete_product')
    if not product:
        return jsonify({"Error": "Not found"}), 404
    if vendor_id == product.vendor_id:
        product.delete()
        delete_product_logger.info(f"product: {product.id}, status: success")
        return jsonify({"status": "success"}), 200

    return jsonify({"Error": "Unauthorized, not  your product"}), 403
