#!/usr/bin/python3
"""module for notification schema definition"""

from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey


class Notification(BaseModel, Base):
    """define the Notification Class"""
    __tablename__ = 'notifications'
    vendor_id = Column(String(60), ForeignKey('vendors.id'),
                       nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
