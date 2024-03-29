#!/usr/bin/env python3
"""Manage Reviews
"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship


class Review(BaseModel, Base):
    """Buyers make review on products they have purchased
    """
    __tablename__ = 'reviews'
    buyer_id = Column(String(60), ForeignKey('buyers.id'),
                      nullable=False)
    star_rating = Column(Float, default=5.0)
    text = Column(String(128))
    product_id = Column(String(60), ForeignKey('products.id'),
                        nullable=False)
