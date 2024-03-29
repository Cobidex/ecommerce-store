#!/usr/bin/env python3
"""Manage Buyer model
"""
from models.base_model import Base
from models.user import User
from sqlalchemy import Column, Boolean
from sqlalchemy.orm import relationship


class Buyer(User, Base):
    """Buyers of products
    - Always use kwargs to update a User class, especially the password
    - This enables hashing the password before it is persisted
    """
    __tablename__ = 'buyers'
    profile_complete = Column(Boolean, default=False)
