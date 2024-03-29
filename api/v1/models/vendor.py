#!/usr/bin/python3
"""module for vendor schema definition"""

from models.base_model import BaseModel, Base
from models.user import User
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship


class Vendor(User, Base):
    '''define the Vendor Class
    - Always use kwargs to update a User class, especially the password
    - This enables hashing the password before it is persisted
    '''
    __tablename__ = 'vendors'
    department = Column(String(128))
    level = Column(Integer)
    products = relationship('Product', backref='vendor',
                            cascade='all, delete-orphan')
