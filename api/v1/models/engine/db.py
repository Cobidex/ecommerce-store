#!/usr/bin/python3
"""This module contains the database connection object definition"""
from os import getenv
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base
from models.buyer import Buyer
from models.category import Category
from models.notification import Notification
from models.product import Product
from models.review import Review
from models.vendor import Vendor
from models.order import Order, OrderItem

load_dotenv()

classes = {
    'Buyer': Buyer,
    'Category': Category,
    'Notification': Notification,
    'Product': Product,
    'Review': Review,
    'Vendor': Vendor,
    'Order': Order,
    'OrderItem': OrderItem
}


class DBStorage():
    """Define the storage connection class"""
    __engine = None
    __session = None

    def __init__(self):
        '''
        connection_string = 'postgresql://{}:{}@{}:{}/{}'. format(getenv('DB_USERNAME'),
                                                                  getenv('DB_PASSWORD'),
                                                                  getenv('DB_HOST'),
                                                                  getenv('DB_PORT'),
                                                                  getenv('DB_NAME'))
        '''
        DB_URL = getenv('DATABASE_URL')
        if not DB_URL:
            exit(1)
        connection_string = DB_URL
        self.__engine = create_engine(connection_string, pool_pre_ping=True)

    def all(self, cls=None, **querry):
        """gets objects of a specific class
        If cls is None: queries all types of objects."""

        per_page = querry.get('per_page')
        offset = querry.get('offset')
        objs = []
        if cls is None:
            for a_class in classes.values():
                objs += self.__session.query(a_class)\
                    .limit(per_page)\
                    .offset(offset).all()
        elif cls in classes.values():
            objs = self.__session.query(cls)\
                .limit(per_page)\
                .offset(offset).all()
        else:
            return dict()

        # Modify objects so that the result will be a dictionary of
        # key, value pairs where
        # key = <class name>.<object id>
        # value = object
        objs_dict = dict()
        for value in objs:
            key = type(value).__name__ + '.' + value.id
            objs_dict.update({key: value})

        return objs_dict

    def new(self, obj):
        """"adds an object to current database session"""
        self.__session.add(obj)

    def save(self):
        """commits changes to the current database session"""
        self.__session.commit()

    def delete(self, obj=None):
        """delete from the current session"""
        if obj:
            self.__session.delete(obj)

    def reload(self):
        """creates a new session"""
        Base.metadata.create_all(self.__engine)

        # Create current database session
        # The option expire_on commit must be False
        # and scoped_session is used to ensure the session is thread-safe
        session = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(session)
        self.__session = Session()

    def close(self):
        """closes the current session"""
        self.__session.close()

    def get(self, cls, id):
        """retrieves one object
        cls: The class of the object to retrieve
        id: unique id of the object to retrieve
        """
        cls_list = list(classes.values())
        if cls not in cls_list:
            return (None)

        obj = self.__session.query(cls).filter(cls.id == id).first()
        if not obj:
            return (None)
        return (obj)

    def get_reviews(self, cls, product_id, **querry):
        """retrieves product reviews
        cls: The class of the object to retrieve
        id: unique product id of the product to retrieve its reviews
        """
        cls_list = list(classes.values())
        if cls not in cls_list:
            return (None)
        per_page = querry.get('per_page')
        offset = querry.get('offset')

        objs = self.__session.query(cls).filter(cls.product_id == product_id)\
            .limit(per_page).offset(offset).all()
        if not objs:
            return (None)
        return (objs)

    def get_by_category(self, cls, category_id, **querry):
        """retrieves one object
        cls: The class of the object to retrieve
        querry: dictionary with querry parameters to retrieve objects
        """
        cls_list = list(classes.values())
        if cls not in cls_list:
            return (None)

        per_page = querry.get('per_page')
        offset = querry.get('offset')

        objs = self.__session.query(cls).filter(
            cls.category_id == category_id) .limit(per_page).offset(offset).all()
        if not objs:
            return (None)
        return (objs)

    def search_products(self, cls, **querry):
        """retrieves search objects
        cls: The class of the objects to retrieve
        querry: dictionary with querry parameters to retrieve objects
        """
        cls_list = list(classes.values())
        if cls not in cls_list:
            return (None)

        per_page = querry.get('per_page')
        offset = querry.get('offset')
        name = querry.get('name')

        objs = self.__session.query(cls).filter(cls.name.like(f"%{name}%"))\
            .limit(per_page).offset(offset).all()
        if not objs:
            return (None)
        return (objs)

    def get_by_email(self, cls, email):
        """retrieves one object
        cls: The class of the object to retrieve(Vendor | Buyer)
        email: unique email of the user to retrieve
        """
        if cls not in list(classes.values()):
            return (None)

        return self.__session.query(cls).filter(
            cls.email == email).first() or None

    def get_by_buyer(self, cls, buyer_id):
        """retrieves one object
        cls: The class of the object to retrieve(Vendor | Buyer)
        email: unique email of the user to retrieve
        """
        if cls not in list(classes.values()):
            return (None)

        return self.__session.query(cls).filter(
            cls.buyer_id == buyer_id).first() or None

    def get_by_name(self, cls, name):
        """retrieves one object
        cls: The class of the object to retrieve
        name: unique name of the user to retrieve
        """
        if cls not in list(classes.values()):
            return (None)

        return self.__session.query(cls).filter(
            cls.name == name).first() or None

    def get_by_name(self, cls, name):
        """retrieves one object
        cls: The class of the object to retrieve
        vendor: unique name of the user to retrieve
        """
        if cls not in list(classes.values()):
            return (None)

        return self.__session.query(cls).filter(
            cls.name == name).first() or None

    def count(self, cls=None):
        """
        count the number of objects in storage
        - cls: the class to count its objects 'not string'
        """
        count = 0

        if cls is None:
            for a_class in classes.values():
                obj = self.__session.query(a_class).all()
                count += len(obj)
        else:
            obj = self.__session.query(cls).all()
            count = len(obj)

        return (count)
