#!/usr/bin/env python3
"""Manage products
"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Table, Float
from sqlalchemy.orm import relationship

product_delivery_association = Table(
    'product_delivery_association', Base.metadata,
    Column('product_id', String(60), ForeignKey('products.id')),
    Column('delivery_location_id', String(60),
           ForeignKey('delivery_locations.id'))
)


class Product(BaseModel, Base):
    """Products of vendors for buyers
    """
    __tablename__ = 'products'
    name = Column(String(128), nullable=False)
    description = Column(String(128))
    price = Column(Integer, default=0)  # In kobo
    in_stock = Column(Integer, default=0)
    category_id = Column(String(60), ForeignKey('categories.id'),
                         nullable=False)
    vendor_id = Column(String(60), ForeignKey('vendors.id'),
                       nullable=False)
    photo_urls = Column(JSON, nullable=False)
    reviews = relationship('Review', backref='product',
                           cascade='all, delete-orphan')

    delivery_locations = relationship("DeliveryLocation",
                                      secondary='product_delivery_association',
                                      back_populates="products",
                                      cascade="all, delete",
                                      passive_deletes=True)

    def to_dict(self):
        """returns dictionary form of object"""
        my_dict = {
            'id': self.id,
            'description': self.description,
            '__class__': self.__class__.__name__,
            'price': self.price,
            'in_stock': self.in_stock,
            'vendor_id': self.vendor_id,
            'photo_url': self.photo_urls,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        delivery_locations = [location.to_dict()
                              for location in self.delivery_locations]
        my_dict['deliver_locations'] = delivery_locations

        reviews = [review.to_dict() for review in self.reviews]
        my_dict['reviews'] = reviews

        return (my_dict)


class DeliveryLocation(BaseModel, Base):
    __tablename__ = 'delivery_locations'
    address = Column(String(128))
    cost_of_delivery = Column(Integer, default=0)
    products = relationship("Product",
                            secondary='product_delivery_association',
                            back_populates="delivery_locations",
                            cascade="all, delete",
                            passive_deletes=True)

    def to_dict(self):
        """returns dictionary form of object"""
        my_dict = {
            'id': self.id,
            'address': self.address,
            '__class__': self.__class__.__name__,
            'cost_of_delivery': self.cost_of_delivery,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        return my_dict
