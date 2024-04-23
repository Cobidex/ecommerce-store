from sqlalchemy import Integer, String, Column, ForeignKey, Boolean
from models.base_model import BaseModel, Base


class Order(BaseModel, Base):
    """
        manage orders
    """
    __tablename__ = 'orders'
    buyer_id = Column(String(128), ForeignKey('vendors.id'), nullable=False)
    full_name = Column(String(128))
    address = Column(String(128))
    email = Column(String(128), nullable=False)
    city = Column(String(128))
    phone = Column(String(128))
    amount_paid = Column(Integer)
    to_pay = Column(Integer, nullable=False)
    billing_status = Column(Boolean, default=False)


class OrderItem(BaseModel, Base):
    """
        manage items of each order
    """
    __tablename__ = 'order_items'
    order = Column(String(128), ForeignKey('orders.id'))
    vendor_id = Column(String(128), nullable=False)
    product = Column(String(128), ForeignKey('products.id'))
    delivered = Column(Boolean, default=False)
    delivery_code = Column(String(7))
    price = Column(Integer, nullable=False)
    qty = Column(Integer, nullable=False)
    order_token = Column(String(10))
