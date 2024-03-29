#!/usr/bin/python3
"""
    module for the base model to be inherited by all other class
"""
from os import getenv
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, event
from sqlalchemy.ext.declarative import declarative_base
import models


Base = declarative_base()


class BaseModel():
    """the model to be inherited by all other classes
    - Always use kwargs to update a User class, especially the password
    - This enables hashing the password before it is persisted
    """
    id = Column(String(60), primary_key=True)
    created_at = Column(DateTime, nullable=False,
                        default=datetime.now())
    updated_at = Column(DateTime, nullable=False,
                        default=datetime.now())

    def __init__(self, **kwargs):
        if len(kwargs) != 0:
            for key, value in kwargs.items():
                if key in ['verified', 'is_admin', 'is_active']:
                    continue
                setattr(self, key, value)
            self.created_at = datetime.now()
            self.updated_at = self.created_at
            self.id = str(uuid.uuid4())
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = self.created_at

    def __str__(self):
        """returns string representation of object"""
        cls = self.__class__.__name__
        return '[{}] ({}) {}'. format(cls, self.id, self.__dict__)

    def save(self):
        """save current instance in the database"""
        self.updated_at = datetime.now()
        models.storage.new(self)
        models.storage.save()

    def to_dict(self):
        """returns dictionary form of object"""
        my_dict = self.__dict__.copy()
        if 'password' in my_dict:
            del my_dict['password']
        if '_sa_instance_state' in my_dict:
            del my_dict['_sa_instance_state']

        cls = self.__class__.__name__
        my_dict['__class__'] = cls
        my_dict['created_at'] = self.created_at.isoformat()
        my_dict['updated_at'] = self.updated_at.isoformat()
        return (my_dict)

    def delete(self):
        '''deletes the current instance'''
        models.storage.delete(self)
