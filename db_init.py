#!/usr/bin/env python3
"""Initialize the database with some objects
"""
from datetime import datetime, timedelta
from models import storage
from models.photo import Photo
from models.vendor import Vendor
from models.category import Category
from models.product import Product
from models.review import Review
from models.order import Order
from models.buyer import Buyer
from models.payment import Payment


# Photos
ph1 = Photo()
ph1.url = 'https://my_photos.com'
ph1.name = 'Ebube profile'
ph1.save()

ph2 = Photo()
ph2.url = 'https://my_photos.com'
ph2.name = 'Ada profile'
ph2.save()

ph3 = Photo()
ph3.url = 'https://my_photos.com'
ph3.name = 'Stethoscope picture'
ph3.save()


# Vendors
v1 = Vendor(password='pwd')
v1.email = 'ebube@gmail.com'
v1.first_name = 'Ebube'
v1.last_name = 'Onwuta'
v1.photo_id = ph1.id
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
p1.photo_id = ph3.id
p1.save()


# Buyers
b1 = Buyer(password='pwd')
b1.email = 'ada@gmail.com'
b1.first_name = 'Ada'
b1.last_name = 'Zion'
b1.is_male = False
b1.photo_id = ph2.id
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
ord1.delivery_date = datetime.utcnow() + timedelta(days=5)
ord1.save()


# Payments
pay1 = Payment()
pay1.order_id = ord1.id
pay1.amt = (50 * 1000 * 100) + 3000
pay1.transaction_id = 12344     # Obtained from PayStack
pay1.save()
