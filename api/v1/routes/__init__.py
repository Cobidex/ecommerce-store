#!/usr/bin/python3
'''initializing package'''
from flask import Blueprint
app_routes = Blueprint('app_views', __name__)
vendor_routes = Blueprint('vendor_routes', __name__)
buyer_routes = Blueprint('buyer_routes', __name__)
notification_routes = Blueprint('notification_routes', __name__)
category_routes = Blueprint('category_routes', __name__)
product_routes = Blueprint('product_routes', __name__)
review_routes = Blueprint('review_routes', __name__)
cart_routes = Blueprint('cart_routes', __name__)
order_routes = Blueprint('order_routes', __name__)
payement_routes = Blueprint('payment_routes', __name__)

from routes.index import *
from routes.vendor import *
from routes.buyer import *
from routes.cart import *
from routes.notification import *
from routes.category import *
from routes.product import *
from routes.review import *
from routes.review import *
from routes.review import *
