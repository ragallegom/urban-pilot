import functools
import requests
import os
import json
import collections

from werkzeug.exceptions import abort

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flaskr.models.user import RegistrationUser

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():

    form = RegistrationUser(request.form)

    username = form.username.data
    password = form.password.data

    error = None

    if request.method == 'POST':
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
    
        if error is not None:
            flash(error)

    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        middle_name = form.middle_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        zip_code = form.zip_code.data
        city, state = "", ""

        db = get_db()
        
        if error is None:
            try:
                api_key = os.getenv('API_KEY_ZIPCODE')
                units = "degrees"
                api_url = f"https://www.zipcodeapi.com/rest/{api_key}/info.json/{zip_code}/{units}"

                response = requests.get(api_url)
                
                if "city" in response.json() and "state" in response.json():
                    data = response.json()
                    city = data['city']
                    state = data['state']

                db.execute(
                    "INSERT INTO user (first_name, middle_name, last_name, username, email, password, zip_code, city, state) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (first_name, middle_name, last_name, username, email, generate_password_hash(password), zip_code, city, state),
                )
                db.commit()
                
                flash('Thanks for registering')
            except db.IntegrityError as e:
                error = f"User {username} or {email} is already registered"
            else:
                if g.user is not None:
                    return redirect(url_for('blog.index'))
                return redirect(url_for("auth.login"))
        
        flash(error)

    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
    
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view

@bp.route('/user/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    user = get_user(id)

    form = RegistrationUser(request.form, password = user['password'], confirm = user['password'])

    error = None
    if not form.username.data:
        error = 'Username is required.'

    if error is not None:
        flash(error)
    
    if request.method == 'POST' and form.validate():

        first_name = form.first_name.data
        middle_name = form.middle_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        zip_code = form.zip_code.data
        city, state = "", ""

        db = get_db()
        
        if error is None:
            try:
                api_key = os.getenv('API_KEY_ZIPCODE')
                units = "degrees"
                api_url = f"https://www.zipcodeapi.com/rest/{api_key}/info.json/{zip_code}/{units}"

                response = requests.get(api_url)
                print(response.json())
                
                if "city" in response.json() and "state" in response.json():
                    data = response.json()
                    city = data['city']
                    state = data['state']

                db.execute(
                    "UPDATE user SET first_name = ?, middle_name = ?, last_name = ?, username = ?, email = ?, zip_code = ?, city = ?, state = ? WHERE id = ?",
                    (first_name, middle_name, last_name, username, email, zip_code, city, state, id),
                )
                db.commit()
                
                flash('Update register')
            except db.IntegrityError as e:
                error = f"User {username} or {email} is already registered"
        
        flash(error)

        return redirect(url_for('blog.index'))
    
    form = RegistrationUser(
        id = user['id'],
        first_name = user['first_name'],
        middle_name = user['middle_name'],
        last_name = user['last_name'],
        username = user['username'],
        email = user['email'],
        zip_code =user['zip_code'],
    )

    return render_template('auth/update.html', form=form, post={"id": id})

def get_user(id, check_author=True):
    post = get_db().execute(
        'SELECT *'
        ' FROM user'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"User id {id} doesn't exist.")

    if check_author and post['id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/user/<int:id>/', methods=('GET', 'POST'))
@login_required
def get(id):
    user = get_user(id)

    obj_user = []
    dict_user = collections.OrderedDict()
    dict_user["id"] = user[0]
    dict_user["first_name"] = user[1]
    dict_user["middle_name"] = user[2]
    dict_user["last_name"] = user[3]
    dict_user["email"] = user[4]
    dict_user["username"] = user[5]
    dict_user["zip_code"] = user[7]
    dict_user["city"] = user[8]
    dict_user["state"] = user[9]

    obj_user.append(dict_user)

    response_json = json.dumps(obj_user)

    return response_json