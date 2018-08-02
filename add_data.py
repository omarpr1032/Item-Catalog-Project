#!/usr/bin/env python2
# Import the SqlAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import from the database_setup
from database_setup import Base, User, Category, Item


# Create engine for the database
engine = create_engine('sqlite:///categories.db')

# Bind the engine to the metadata of the Base class
Base.metadata.bind = engine

# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create my user
User = User(name="Administrator", email="admin@gmail.com", picture='')
session.add(User)
session.commit()

# Add categories
category1 = Category(user_id=1, name="Graphic Design")
session.add(category1)
session.commit()

# Category1 Items
item1 = Item(user_id=1, name="Art Edition", description="",
             price="$9.99", category=category1)
session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Basic Design", description="",
             price="$34.99", category=category1)
session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Regular Edition", description="",
             price="$50.99", category=category1)
session.add(item3)
session.commit()

item4 = Item(user_id=1, name="Advanced Edition", description="",
             price="$75.99", category=category1)
session.add(item4)
session.commit()


category2 = Category(user_id=1, name="Business Cards")
session.add(category2)
session.commit()

category3 = Category(user_id=1, name="Banners")
session.add(category3)
session.commit()

category4 = Category(user_id=1, name="Magnet")
session.add(category4)
session.commit()

category5 = Category(user_id=1, name="Flags")
session.add(category5)
session.commit()

print "Categories added successfully"
