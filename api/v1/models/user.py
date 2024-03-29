#!/usr/bin/env python3
from sqlalchemy import (Column, Integer, String, DateTime, event,
                        Boolean, ForeignKey)
from models.base_model import BaseModel
import bcrypt


class User(BaseModel):
    """A base model for users
    - Always use kwargs to update a User class, especially the password
    - This enables hashing the password before it is persisted
    """
    email = Column(String(128), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    first_name = Column(String(128))
    last_name = Column(String(128))
    is_male = Column(Boolean, default=False)     # True for male
    photo_url = Column(String(60))
    location = Column(String(128))
    email_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    def hash_password(self):
        """Hash a password before storing
        """
        self.password = self.password.encode('utf-8')
        salt_bytes = bcrypt.gensalt()
        self.password = bcrypt.hashpw(self.password, salt_bytes).decode('utf-8')

    def compare_pwd(self, password):
        """compares given password to determine match"""
        encoded = password.encode('utf-8')
        return bcrypt.checkpw(encoded, self.password.encode('utf-8')) or None