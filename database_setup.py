#!/usr/bin/env python2
# import the SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# define the declarative_base
Base = declarative_base()


# user class
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        # Return object data in serializeable format
        return{
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
        }


# category class
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    items = relationship("Item", cascade="all, delete-orphan")

    @property
    def serialize(self):
        # Return object data in serializeable format
        return{
            'id': self.id,
            'name': self.name,
        }


# item class
class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=True)
    price = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # return object data in serializeable formatting
        return{
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
        }

# create the database file
engine = create_engine('sqlite:///categories.db')
Base.metadata.create_all(engine)
