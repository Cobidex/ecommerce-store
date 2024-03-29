#!/usr/bin/env python3
"""Manage Categories
"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class Category(BaseModel, Base):
    """Category of products
    """
    __tablename__ = 'categories'
    name = Column(String(128), nullable=False, unique=True)
    products = relationship('Product', backref='category',
                            cascade='all, delete-orphan')
