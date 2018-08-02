#!/usr/bin/env python2
# import session as login_session (Needs set a secret_key)
# import render_template to generates html content
# import url_for for template links
# import jsonify to get serializeable json format
# import request to obtain the request.method type
# import redirect
# impot flash
# import make_response for google disconnect
from flask import Flask, session as login_session, render_template, \
    url_for, jsonify, request, redirect, flash, make_response

# import create_engine and sessionmaker to connect to db and asc  the table
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

# import classes from database_setup
from database_setup import Base, User, Category, Item

# import random and string for the state login_session
import random
import string

# import json to open the client_secrets.json filter_by
import json

# import for OAuth Google Login
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests

# instance the flask app
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "CatalogProject"

# connect to Database and create database session
engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# login page and create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits)for x in xrange(32))
    login_session['state'] = state

    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# google login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        # print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already'
                                            ' connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h2 class="inline">Welcome, '
    output += login_session['username']
    output += '!</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 60px; height: 60px;border-radius: 30px;' \
              '-webkit-border-radius: 30px;-moz-border-radius: 30px;"> '
    # flash("you are now logged in as %s" % login_session['username'])
    # print "done!"
    return output


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


# Google disconnect
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                                            'Failed to revoke token for '
                                            'given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# read categories, home
@app.route('/')
@app.route('/category')
def showCategories():
    # categories menu
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('categories.html', categories=categories)


# add category
@app.route('/category/new', methods=['GET', 'POST'])
def newCategory():
    # login check
    if 'username' not in login_session:
        return redirect('/login')
    # categories menu
    categories = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()

        return redirect(url_for('showCategories', categories=categories))
    else:
        return render_template('newCategory.html', categories=categories)


# delete category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    # categories menu
    categories = session.query(Category).order_by(asc(Category.name))
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    # login check
    if 'username' not in login_session:
        return redirect('/login')
    # autorization check
    if categoryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized"
        " to delete this category. Please create your own category in order "
        "to delete.');}</script><body onload='myFunction()'>"

    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('showCategories', categories=categories))
    else:
        return render_template('deleteCategory.html', categories=categories,
                               category=categoryToDelete)


# edit category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    # categories menu
    categories = session.query(Category).order_by(asc(Category.name))
    editedCategory = session.query(Category).filter_by(id=category_id).one()
    # login check
    if 'username' not in login_session:
        return redirect('/login')
    # autorization check
    if editedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized"
        " to edit this category. Please create your own category in order to"
        " edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            return redirect(url_for('showCategories', categories=categories))
    else:
        return render_template('editCategory.html', categories=categories,
                               category=editedCategory)


# read items
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/items/')
def showItems(category_id):
    # categories menu
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()

    return render_template('items.html', items=items, categories=categories,
                           category=category)


# add items
@app.route('/category/<int:category_id>/items/new/', methods=['GET', 'POST'])
def newItem(category_id):
    # categories menu
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(id=category_id).one()
    # login_check
    if 'username' not in login_session:
        return redirect('/login')
    # autorization check
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized"
        " to add items. Please create your own category in order to add.');}"
        "</script><body onload='myFunction()'>"

    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       price=request.form['price'], category_id=category_id,
                       user_id=1)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItems', categories=categories,
                                category_id=category_id))
    else:
        return render_template('newItem.html', categories=categories,
                               category=category)


# delete items
@app.route('/category/<int:category_id>/items/<int:item_id>/delte',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    # categories menu
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    # login_check
    if 'username' not in login_session:
        return redirect('/login')
    # autorization check
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized"
        " to edit this item. Please create your own category in order to "
        "delete.');}</script><body onload='myFunction()'>"

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', categories=categories,
                        category_id=category_id))
    else:
        return render_template('deleteItem.html', categories=categories,
                               item=itemToDelete, category=category)


# edit items
@app.route('/category/<int:category_id>/items/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    # categories menu
    categories = session.query(Category).order_by(asc(Category.name))
    editedItem = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    # login_check
    if 'username' not in login_session:
        return redirect('/login')
    # autorization check
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized"
        " to edit this item. Please create your own category in order"
        " to edit.');}</script><body onload='myFunction()'>"

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']

        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItems', categories=categories,
                        category_id=category_id))
    else:
        return render_template('editItem.html', categories=categories,
                               category_id=category_id, item_id=item_id,
                               item=editedItem, category=category)


# view all users on database API
@app.route("/allusers/JSON")
def view_users():
    users = session.query(User).all()
    return jsonify(users=[u.serialize for u in users])


# json show categories information API
@app.route('/category/JSON')
def view_categories():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


# show category items information API
@app.route('/category/<int:category_id>/JSON')
def view_category_items(category_id):
    category_items = session.query(Item).filter_by(category_id=category_id)
    return jsonify(category_items=[i.serialize for i in category_items])

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
