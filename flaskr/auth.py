import functools
import requests
import os

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
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
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