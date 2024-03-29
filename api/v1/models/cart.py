#!/usr/bin/env python3

from lib.utils import verify_token, get_token
from lib.utils import verify_token
from services.redis import redisClient

class Cart:
    """
        class to manage shopping items
    """

    def __init__(self, request, user):
        cart_token = redisClient.get(f"carts_{user.get('id')}")
        cart = verify_token(cart_token)
        if not cart:
            self.cart = {"grand_total": 0, "number_of_items": 0}
            cart_token = get_token(self.cart.copy())
            key = f"carts_{user.get('id')}"
            redisClient.set(key, cart_token)
        else:
            self.cart = cart


    def grand_total(self, cart):
        return sum(item['total'] for item in cart.values() if isinstance(item, dict) and 'total' in item)
    
    def total_qty(self, cart):
        return sum(item['qty'] for item in cart.values() if isinstance(item, dict) and 'qty' in item)

    def add(self, product, qty, delivery_price, user):
        cart_item = {
            "vendor_id": product.vendor_id,
            "name": product.name,
            "price": product.price,
            "qty": qty,
            "delivery_price": delivery_price,
            "total": qty * product.price + delivery_price
        }

        self.cart[product.id] = cart_item
        cart_items = self.summary(self.cart)
        cart_token = get_token(cart_items)
        key = f"carts_{user.get('id')}"
        redisClient.set(key, cart_token)
        return cart_items
              
    def summary(self, cart):
        cart["grand_total"] = self.grand_total(cart)
        cart['number_of_items'] = self.total_qty(cart)
        cart_items = cart.copy()
        return cart_items
    
    def remove(self, product_id, user):
        self.cart.pop(product_id)
        cart = self.summary(self.cart)
        cart_token = get_token(cart)
        redisClient.set(f"carts_{user.get('id')}", cart_token)
        return cart
    
    def get_cart(self, user):
        cart_token = redisClient.get(f"carts_{user.get('id')}")
        return verify_token(cart_token)
    
    def clear_cart(self, user):
        self.cart = {"grand_total": 0, "number_of_items": 0}
        cart_token = get_token(self.cart.copy())
        key = f"carts_{user.get('id')}"
        redisClient.set(key, cart_token)