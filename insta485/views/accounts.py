"""
Insta485 account view.

URLs include:
/accounts/login/
/accounts/create/
/accounts/delete/
/accounts/edit/
/accounts/password/
/accounts/logout/
"""
import flask
import insta485
from insta485.views.helpers import gen_hash
from insta485.views.helpers import gen_uuid
from insta485.views.helpers import user_exists
from insta485.views.helpers import setup_queries
from insta485.views.helpers import delete_img
from insta485.views.helpers import delete_user_img


# ---------------------- LOGIN ----------------------
@insta485.app.route('/accounts/login/')
def get_account_login():
    """Display /accounts/login/ route."""
    # Redirect to home page if logged in
    if 'logname' in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    # Set logname to blank
    context = {"logname": ""}
    return flask.render_template("login.html", **context)


def post_account_login():
    """Log in user and set session."""
    login_username = flask.request.form['username']
    login_password = flask.request.form['password']
    if not login_username or not login_password:
        flask.abort(400)

    # query stored password hash in database
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
        flask.abort(403)

    # database store: sha512 $ salt $ hash(salt + password)
    password = result[0]["password"]
    hash_alg = password.split('$')[0]
    salt = password.split('$')[1]
    password_attempt = gen_hash(login_password, hash_alg, salt)

    # success
    if password == password_attempt:
        flask.session['logname'] = login_username
    # fail
    else:
        flask.abort(403)


# ---------------------- CREATE ----------------------
@insta485.app.route('/accounts/create/')
def get_account_create():
    """Display account creation page."""
    # Redirect to accounts edit page if logged in
    if 'logname' in flask.session:
        return flask.redirect("/accounts/edit/")

    # Set logname to blank
    context = {"logname": ""}
    return flask.render_template("create.html", **context)


def post_account_create():
    """Create account and create session for user."""
    username = flask.request.form["username"]
    password = flask.request.form["password"]
    fullname = flask.request.form["fullname"]
    email = flask.request.form["email"]
    fileobj = flask.request.files["file"]

    if (not username or not password or not fullname
            or not email or not fileobj):
        flask.abort(400)

    # Connect to database
    connection = insta485.model.get_db()

    # make sure user doesn't exist
    if user_exists(connection, username):
        flask.abort(409)

    password_db_string = gen_hash(password)
    uuid_basename = gen_uuid(fileobj)

    connection.execute(
        "insert into users(username, fullname, email, filename, password) "
        "values(?, ?, ?, ?, ?) ",
        (username, fullname, email, uuid_basename, password_db_string)
    )

    flask.session['logname'] = username


# ---------------------- DELETE ----------------------
@insta485.app.route('/accounts/delete/')
def get_account_delete():
    """Display delete account page."""
    if 'logname' not in flask.session:
        return flask.redirect('/accounts/login/')

    context = {"logname": flask.session['logname']}
    return flask.render_template("delete.html", **context)


def post_account_delete():
    """Delete user's account."""
    if 'logname' not in flask.session:
        flask.abort(403)

    logname, connection = setup_queries()
    delete_user_img(logname, connection)

    # Get user's posts files
    cur = connection.execute(
        "select filename "
        "from posts "
        "where owner = ?;",
        (logname, )
    )
    post_files = cur.fetchall()

    # Delete user's posts files
    for post in post_files:
        delete_img(post['filename'])

    # Remove user from database
    connection.execute(
        "delete from users "
        "where username = ?;",
        (logname, )
    )
    flask.session.clear()


# ---------------------- EDIT ----------------------
@insta485.app.route('/accounts/edit/')
def get_account_edit():
    """Display edit account page."""
    # Redirect to accounts edit page if logged in
    if 'logname' not in flask.session:
        return flask.redirect("/accounts/login/")

    logname, connection = setup_queries()

    cur = connection.execute(
        "select username, fullname, email, filename as owner_img_url "
        "from users "
        "where username = ?;",
        (logname, )
    )

    user_info = cur.fetchall()

    assert len(user_info) == 1

    # Set logname to blank
    context = {"logname": logname, "user": user_info[0]}
    return flask.render_template("edit.html", **context)


def post_account_edit():
    """Edit account."""
    if 'logname' not in flask.session:
        flask.abort(403)

    logname = flask.session['logname']

    fullname = flask.request.form['fullname']
    email = flask.request.form['email']
    fileobj = flask.request.files['file']

    if not fullname or not email:
        flask.abort(400)

    connection = insta485.model.get_db()

    # file to be replaced
    if fileobj:
        delete_user_img(logname, connection)

        # update user info
        uuid_basename = gen_uuid(fileobj)
        connection.execute(
            "update users "
            "set fullname = ?, email = ?, filename = ? "
            "where username = ?;",
            (fullname, email, uuid_basename, logname)
        )
    # no file to replace
    else:
        # update user info
        connection.execute(
            "update users "
            "set fullname = ?, email = ? "
            "where username = ?;",
            (fullname, email, logname)
        )


# ---------------------- UPDATE PASSWORD ----------------------


@insta485.app.route('/accounts/password/')
def get_account_password():
    """Display password change page."""
    # Redirect to login page if not logged in
    if 'logname' not in flask.session:
        return flask.redirect("/accounts/login/")
    logname = flask.session['logname']

    context = {"logname": logname}
    return flask.render_template("password.html", **context)


def post_account_update_password():
    """Update password for user."""
    if 'logname' not in flask.session:
        flask.abort(403)
    logname = flask.session['logname']

    password = flask.request.form['password']
    new_password1 = flask.request.form['new_password1']
    new_password2 = flask.request.form['new_password2']

    if not password or not new_password1 or not new_password2:
        flask.abort(400)

    connection = insta485.model.get_db()

    # get old password
    cur = connection.execute(
        "select password "
        "from users "
        "where username = ?;",
        (logname, )
    )
    result = cur.fetchall()

    old_password = result[0]['password']
    hash_alg = old_password.split('$')[0]
    old_salt = old_password.split('$')[1]
    password_attempt = gen_hash(password, hash_alg, old_salt)

    # checking user password correct
    if old_password != password_attempt:
        flask.abort(403)

    # checking is new passwords same
    if new_password1 != new_password2:
        flask.abort(401)

    # update user password
    password_db_string = gen_hash(new_password1)
    cur = connection.execute(
        "update users "
        "set password = ? "
        "where username = ?;",
        (password_db_string, logname)
    )


# ---------------------- LOGOUT ----------------------
@insta485.app.route('/accounts/logout/', methods=['POST'])
def post_account_logout():
    """Log user out of session."""
    # POST-only route for handling logout requests
    flask.session.clear()
    return flask.redirect("/accounts/login/")


@insta485.app.route('/accounts/', methods=['POST'])
def post_accounts():
    """Handle accounts posts."""
    redirect_to = flask.request.args.get('target')
    if redirect_to is None:
        redirect_to = "/"

    action = flask.request.form['operation']
    if action == "login":
        post_account_login()
    elif action == "create":
        post_account_create()
    elif action == "delete":
        post_account_delete()
    elif action == "edit_account":
        post_account_edit()
    elif action == "update_password":
        post_account_update_password()
    else:
        pass

    return flask.redirect(redirect_to)
