#!/usr/bin/env python3
"""Manage Categories
"""
from flask import jsonify, request
from routes import category_routes
from models import storage
from models.category import Category
from models.product import Product
from middlewares.admin_middleware import admin_only

@category_routes.get('/categories')
def GET_categories():
    page_number = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page_number - 1) * per_page
    querry = {"offset": offset, "per_page": per_page}
    categories = [category.to_dict() for category in\
                  storage.all(Category, **querry).values()]
    return jsonify(categories)


@category_routes.get('/categories/<category_id>/products')
def GET_category_products(category_id):
    page_number = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page_number - 1) * per_page
    querry = {"offset": offset, "per_page": per_page}

    products = storage.get_by_category(Product, category_id, **querry)

    if products and len(products) > 0:
        product_list = [prod.to_dict() for prod in products]
        return jsonify(product_list), 200
    return jsonify({"Error": "Not found"}), 404


@category_routes.post('/categories')
@admin_only
def CREATE_catagory():
    field = request.get_json()

    if not field:
        return jsonify({"Error": "Not a valid json"})
    exists = storage.get(Category, field.get('name'))
    if exists:
        return jsonify({"Error": "Category already exists"}), 403
    obj = {"name": field.get('name')}
    new_category = Category(**obj)
    new_category.save()
    return jsonify(new_category.to_dict())


@category_routes.patch('/category/<category_id>')
def Rename_category(category_id):
    fields = request.get_json()
    if not fields.get('name'):
        return jsonify({"Error": "Not a valid json"})
    category = storage.get(Category, category_id)
    if category:
        category['name'] = fields.get('name')
        category.save()
        return jsonify(category.to_dict()), 200
    
    return jsonify({"Error": "Not found"}), 404