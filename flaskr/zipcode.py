import json
import collections

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('zipcode', __name__)

@bp.route('/zipcode')
@login_required
def index():
    db = get_db()
    zip_code = db.execute(
        'SELECT *, COUNT(*) as users'
        ' FROM user'
        ' GROUP BY zip_code;'
    ).fetchall()

    states = db.execute(
        'SELECT state, zip_code, city, COUNT(*) as users'
        ' FROM user as u'
        ' GROUP BY state, zip_code'
        ' ORDER BY state DESC'
    ).fetchall()

    object_list = []

    for row in states:
        d = collections.OrderedDict()
        d["state"] = row[0]
        d["zip_code"] = row[1]
        d["city"] = row[2]
        d["users"] = row[3]
        object_list.append(d)

    object_zip = []
    current_state = ""
    max_user = 0
    temp = {}
    for index, obj in enumerate(object_list):
        if index != len(object_list)-1:
            if current_state == "":
                max_user = obj['users']
                temp = obj
            elif current_state != obj['state'] and current_state != "":
                object_zip.append(temp)
                max_user = 0
                temp = obj
            else:
                if obj['users'] > max_user:
                    max_user = obj['users']
                    temp = obj  
            current_state = obj['state']
        else:
            if current_state != obj['state']:
                object_zip.append(obj)
            else:
                if obj['users'] > max_user:
                    object_zip.append(obj)
                else:
                    object_zip.append(temp)
    
    db.execute(
        'DELETE FROM zip_code;'
    )
    db.commit()

    for zip in object_zip:
        db.execute(
            "INSERT INTO zip_code (zip_code, users, city, state) VALUES (?, ?, ?, ?)",
            (zip['zip_code'], zip['users'], zip['city'], zip['state']),
        )
        db.commit()

    return render_template('zipcode/index.html', posts=zip_code, states=object_zip)

@bp.route('/zipcode/calculate')
@login_required
def calculate_zip_code():
    db = get_db()

    states = db.execute(
        'SELECT state, zip_code, city, COUNT(*) as users'
        ' FROM user as u'
        ' GROUP BY state, zip_code'
        ' ORDER BY state DESC'
    ).fetchall()

    object_list = []

    for row in states:
        d = collections.OrderedDict()
        d["state"] = row[0]
        d["zip_code"] = row[1]
        d["city"] = row[2]
        d["users"] = row[3]
        object_list.append(d)

    object_zip = []
    current_state = ""
    max_user = 0
    temp = {}
    for index, obj in enumerate(object_list):
        if index != len(object_list)-1:
            if current_state == "":
                max_user = obj['users']
                temp = obj
            elif current_state != obj['state'] and current_state != "":
                object_zip.append(temp)
                max_user = 0
                temp = obj
            else:
                if obj['users'] > max_user:
                    max_user = obj['users']
                    temp = obj  
            current_state = obj['state']
        else:
            if current_state != obj['state']:
                object_zip.append(obj)
            else:
                if obj['users'] > max_user:
                    object_zip.append(obj)
                else:
                    object_zip.append(temp)

    return redirect(url_for('zipcode.index'))