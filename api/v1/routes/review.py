#!/usr/bin/env python3

"""module for review routes"""
from flask import jsonify, request
from routes import review_routes
from lib.utils import verify_token
from models import storage
from models.review import Review
from models.product import Product
from middlewares.auth_middleware import login_required
from middlewares.buyer_middleware import buyers_only
from services.logger import (
    get_all_reviews_logger,
    post_product_review_logger,
    update_product_review,
    delete_product_review_logger
)


@review_routes.get('/products/<product_id>/reviews')
def GET_all_reviews(product_id):
    page_number = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page_number - 1) * per_page
    querry = {"offset": offset, "per_page": per_page}
    reviews = storage.get_reviews(Review, product_id, **querry)
    reviews = [review.to_dict() for review in reviews]
    get_all_reviews_logger.info(f"reviews: {product_id}, status: success")
    return jsonify(reviews)


@review_routes.post('/products/<product_id>/reviews')
@buyers_only
def POST_review(user, product_id):
    fields = request.get_json()
    review = {}
    review['text'] = fields.get('text')
    if not fields:
        return jsonify({"Error": "Not a valid json"}), 400

    product = storage.get(Product, product_id)
    if not product:
        return jsonify({"Error": "Product not found"}), 404

    review['buyer_id'] = user.get('id')
    review['product_id'] = product.id

    new_review = Review(**review)
    new_review.save()
    post_product_review_logger.info(f"review: {new_review.id}, status: success")


@review_routes.patch('/reviews/<review_id>')
@buyers_only
def UPDATE_review(user, review_id):
    fields = request.get_json()
    text = fields.get('text')

    if not fields:
        return jsonify({"Error": "Not a valid json"}), 400

    review = storage.get(Review, review_id)
    if not review:
        return jsonify({"Error": "Not found"}), 404

    if user.get('id') != review.buyer_id:
        return jsonify({"Error": "unauthorized"}), 403
    
    review.text = text
    review.save()
    update_product_review.info(f"review: {review.id}, status: success")
    return jsonify(review.to_dict()), 200


@review_routes.delete('/reviews/<review_id>')
@buyers_only
def DELETE_review(user, review_id):

    review = storage.get(review, review_id)
    if not review:
        return jsonify({"Error": "Not found"}), 404
    if user.get('id') == review.buyer_id:
        review.delete()
        delete_product_review_logger.info(f"review: {review_id}, status: success")
        return jsonify({"status": "success"}), 200

    return jsonify({"Error": "Unauthorized"}), 403
