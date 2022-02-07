"""Helper functions for REST API."""
import flask
import insta485
from insta485.views.helpers import gen_hash
from insta485.views.helpers import user_exists
from insta485.views.helpers import setup_queries


def get_username():
    """Return username or None if unauthenticated."""
    if 'logname' in flask.session:
        return flask.session['logname']

    if (not flask.request.authorization or 
            'username' not in flask.request.authorization 
            or 'password' not in flask.request.authorization):
        return None
    login_username = flask.request.authorization['username']
    login_password = flask.request.authorization['password']

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (login_username,)
    )
    result = cur.fetchall()

    # username doesn't have an account
    if len(result) == 0:
        return None

    # database store: sha512 $ salt $ hash(salt + password)
    password = result[0]["password"]
    hash_alg = password.split('$')[0]
    salt = password.split('$')[1]
    password_attempt = gen_hash(login_password, hash_alg, salt)

    # success
    if password == password_attempt:
        return login_username
    else:
        return None
