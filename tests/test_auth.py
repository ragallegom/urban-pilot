import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register',
        data=dict([('first_name', 'aaa'), ('middle_name', 'aaa'), ('last_name', 'aaa'), ('username', 'aaaa'), ('email', 'rgallegomoreno@gmail.com'), ('password', 'a'), ('confirm', 'a'), ('zip_code', '00501')])
    )

    assert response.headers["Location"] == "/auth/login"

    response = client.post(
        '/auth/register',
        data=dict([('first_name', 'aaa'), ('middle_name', 'aaa'), ('last_name', 'aaa'), ('username', 'aaaa'), ('email', 'rgallegomoreno@gmail.com'), ('password', 'a'), ('confirm', 'a'), ('zip_code', '00501')])
    )

    assert b'is already registered' in response.data 

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'aaaa'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('aaaa', '', b'Password is required.'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data=dict([('first_name', 'aaa'), ('middle_name', 'aaa'), ('last_name', 'aaa'), ('username', username), ('email', 'test1@gmail.com'), ('password', password), ('confirm', 'a'), ('zip_code', 'aaaaa')])
    )
    assert message in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

def test_update(client, auth, app):
    auth.login()
    response = client.post(
        'auth/user/1/update',
        data=dict([('first_name', 'bbb'), ('middle_name', 'aaa'), ('last_name', 'aaa'), ('username', 'aaaa'), ('email', 'rgallegomoreno@gmail.com'), ('password', 'a'), ('confirm', 'a'), ('zip_code', 'aaaaa')])
    )

    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id = 1').fetchone()
        assert user['first_name'] == 'bbb'

def test_register_with_zip_code(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register',
        data=dict([('first_name', 'aaa'), ('middle_name', 'aaa'), ('last_name', 'aaa'), ('username', 'bbbb'), ('email', 'bbbb@gmail.com'), ('password', 'a'), ('confirm', 'a'), ('zip_code', '00501')])
    )

    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'bbbb' AND city <> ''",
        ).fetchone() is not None

def test_register_without_zip_code(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register',
        data=dict([('first_name', 'aaa'), ('middle_name', 'aaa'), ('last_name', 'aaa'), ('username', 'cccc'), ('email', 'cccc@gmail.com'), ('password', 'a'), ('confirm', 'a'), ('zip_code', '050030')])
    )

    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'cccc' AND city = ''",
        ).fetchone() is not None

def test_update_with_zip_code(client, auth, app):
    auth.login()
    response = client.post(
        'auth/user/1/update',
        data=dict([('first_name', 'bbb'), ('middle_name', 'aaa'), ('last_name', 'aaa'), ('username', 'aaaa'), ('email', 'rgallegomoreno@gmail.com'), ('password', 'a'), ('confirm', 'a'), ('zip_code', '00501')])
    )

    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id = 1').fetchone()
        assert user['first_name'] == 'bbb'

def test_update_failed(client, auth, app):
    auth.login()
    response = client.post(
        'auth/user/1/update',
        data=dict([('first_name', 'bbb'), ('middle_name', 'aaa'), ('last_name', 'aaa'), ('username', ''), ('email', 'rgallegomoreno@gmail.com'), ('password', 'a'), ('confirm', 'a'), ('zip_code', '00501')])
    )

    assert b'Username is required.' in response.data

@pytest.mark.parametrize('path', (
    '/auth/user/3/update',
    '/3/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

def test_author_required(app, client, auth):
    auth.login()
    # current user can't modify other user's post
    assert client.post('/auth/user/2/update').status_code == 403
    assert client.post('/2/delete').status_code == 403