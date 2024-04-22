#!/usr/bin/env python3
"""Initialize the database with some objects
"""
from datetime import datetime, timedelta
from api.v1.models import storage
from api.v1.models.vendor import Vendor
from api.v1.models.category import Category
from api.v1.models.product import Product
from api.v1.models.review import Review
from api.v1.models.order import Order
from api.v1.models.buyer import Buyer


# Vendors
v1 = Vendor(password='pwd')
v1.email = 'ebube@gmail.com'
v1.first_name = 'Ebube'
v1.last_name = 'Onwuta'
v1.is_male = True
v1.department = 'Medicine and surgery'
v1.level = 200
v1.location = '6 Ezekwesili street Abakpa Nike'
v1.save()


# Categories
c1 = Category()
c1.name = 'Health'
c1.save()


# Products
p1 = Product()
p1.name = 'Stethoscope'
p1.description = 'Von neuman stethoscope'
p1.price = 50 * 1000 * 100  # In kobo (NGN)
p1.qty = 7
p1.category_id = c1.id
p1.vendor_id = v1.id
p1.save()


# Buyers
b1 = Buyer(password='pwd')
b1.email = 'ada@gmail.com'
b1.first_name = 'Ada'
b1.last_name = 'Zion'
b1.is_male = False
b1.location = 'Mountain Zion'
b1.save()


# Reviews
r1 = Review()
r1.buyer_id = b1.id
r1.product_id = p1.id
r1.text = 'It was a very good product'
r1.save()


# Orders
ord1 = Order()
ord1.product_id = p1.id
ord1.buyer_id = b1.id
ord1.qty = p1.qty - 1
ord1.status = 'pending'
ord1.notes = 'I need it as soon as possible'
ord1.delivery_date = datetime.now() + timedelta(days=5)
ord1.save()
