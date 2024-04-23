#!/usr/bin/python3
'''module contains my app'''
from flask import Flask, Blueprint, jsonify, make_response
from flask_cors import CORS
from os import getenv
from routes import app_routes
from routes import vendor_routes
from routes import buyer_routes
from routes import notification_routes
from routes import category_routes
from routes import product_routes
from routes import review_routes
from routes import cart_routes
from routes import order_routes
from routes import payement_routes
from services.email import email_sender

app = Flask(__name__)

app.config['MAIL_SERVER'] = getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = getenv('EMAIL_SENDER')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

app.register_blueprint(app_routes, url_prefix='/api/v1')
app.register_blueprint(vendor_routes, url_prefix='/api/v1/')
app.register_blueprint(buyer_routes, url_prefix='/api/v1/')
app.register_blueprint(notification_routes, url_prefix='/api/v1/')
app.register_blueprint(category_routes, url_prefix='/api/v1/')
app.register_blueprint(product_routes, url_prefix='/api/v1/')
app.register_blueprint(review_routes, url_prefix='/api/v1/')
app.register_blueprint(cart_routes, url_prefix='/api/v1/')
app.register_blueprint(order_routes, url_prefix='api/v1/')
app.register_blueprint(payement_routes, url_prefix='/api/v1/')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

if __name__ == '__main__':
    email_sender.initialize(app)
    app.run(host=getenv('API_HOST', '0.0.0.0'),
            port=getenv('API_PORT', 5000), threaded=True)
