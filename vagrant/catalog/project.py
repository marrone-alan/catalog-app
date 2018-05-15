from flask import (Flask, render_template, request, redirect, jsonify,
                   url_for)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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
        print "Token's client ID does not match app's."
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

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('catalogMenu'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given'
                                 ' user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('catalogMenu'))


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
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


@app.route('/JSON')
def categoriesJSON():
    categories = session.query(Categories).all()
    for c in categories:
        items = session.query(Item).filter_by(
            categories_id=c.id).all()
        c.items = [item.serialize for item in items]
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/categories/<int:categories_id>/JSON')
def itemsJSON(categories_id):
    items = session.query(Item).filter_by(
        categories_id=categories_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/')
def catalogMenu():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    isLogged = False
    # check if a user is logged
    if 'username' in login_session:
        isLogged = True
    categories = session.query(Categories).all()
    items = session.query(Item).order_by('id DESC').limit(10)
    return render_template('menu.html', categories=categories, items=items,
                           STATE=state, isLogged=isLogged)


@app.route('/categories/new/', methods=['GET', 'POST'])
def newCategory():
    # if the user is not logged in, redirect to the home page
    if 'username' not in login_session:
        return redirect('/')
    if request.method == 'POST':
        newCategory = Categories(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('catalogMenu'))
    else:
        return render_template('newcategory.html')


@app.route('/categories/<int:categories_id>/', methods=['GET'])
def categoryItems(categories_id):
    category = session.query(Categories).filter_by(id=categories_id).one()
    items = session.query(Item).filter_by(categories_id=categories_id).all()
    isCreator = False
    # only shows the options if the user is the creator
    if 'username' in login_session:
        if category.user_id == login_session['user_id']:
            isCreator = True
    return render_template('items.html', items=items,
                           categories_id=categories_id, category=category,
                           isCreator=isCreator)


@app.route('/categories/<int:categories_id>/edit', methods=['GET', 'POST'])
def editCategory(categories_id):
    if 'username' not in login_session:
            return redirect('/')
    editedCategory = session.query(
        Categories).filter_by(id=categories_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        # only edit if the user is the creator
        if editedCategory.user_id == login_session['user_id']:
            session.add(editedCategory)
            session.commit()
        return redirect(url_for('categoryItems', categories_id=categories_id))
    else:
        category = session.query(Categories).filter_by(id=categories_id).one()
        return render_template('editcategory.html', category=category,
                               categories_id=categories_id)


@app.route('/categories/<int:categories_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(categories_id):
    if 'username' not in login_session:
            return redirect('/')
    categoryToDelete = session.query(Categories).filter_by(
                                id=categories_id).one()
    if request.method == 'POST':
        # only delete if the user is the creator
        if categoryToDelete.user_id == login_session['user_id']:
            itensToDelete = session.query(Item).filter_by(
                            categories_id=categories_id).all()
            for item in itensToDelete:
                session.delete(item)
            session.delete(categoryToDelete)
            session.commit()
        return redirect(url_for('catalogMenu'))
    else:
        category = session.query(Categories).filter_by(id=categories_id).one()
        return render_template('deletecategory.html', category=category,
                               categories_id=categories_id)


@app.route('/categories/<int:categories_id>/<int:item_id>/details',
           methods=['GET'])
def detailItem(categories_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    isCreator = False
    if 'username' in login_session:
        if item.user_id == login_session['user_id']:
            isCreator = True
    return render_template('detail.html', item=item,
                           categories_id=categories_id, isCreator=isCreator)


@app.route('/categories/<int:categories_id>/new', methods=['GET', 'POST'])
def newItem(categories_id):
    if 'username' not in login_session:
            return redirect('/')
    if request.method == 'POST':
        if request.form['name']:
            newItem = Item(
                name=request.form['name'],
                description=request.form['description'],
                categories_id=categories_id, user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
        return redirect(url_for('categoryItems', categories_id=categories_id))
    else:
        category = session.query(Categories).filter_by(id=categories_id).one()
        return render_template('newitem.html', categories_id=categories_id,
                               category=category)


@app.route('/categories/<int:categories_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(categories_id, item_id):
    if 'username' not in login_session:
            return redirect('/')
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if editedItem.user_id == login_session['user_id']:
            session.add(editedItem)
            session.commit()
        return redirect(url_for('catalogMenu', categories_id=categories_id))
    else:
        category = session.query(Categories).filter_by(id=categories_id).one()
        return render_template(
            'edititem.html', categories_id=categories_id, item_id=item_id,
            item=editedItem, category=category)


@app.route('/categories/<int:categories_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(categories_id, item_id):
    if 'username' not in login_session:
            return redirect('/')
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if itemToDelete.user_id == login_session['user_id']:
            session.delete(itemToDelete)
            session.commit()
        return redirect(url_for('catalogMenu', categories_id=categories_id))
    else:
        category = session.query(Categories).filter_by(id=categories_id).one()
        return render_template('deleteitem.html', item=itemToDelete,
                               categories_id=categories_id, category=category)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
