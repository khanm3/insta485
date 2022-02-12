"""
Insta485 follow.

URLs include:
/users/<username>/followers/
/users/<username>/following/
/following/
"""
import flask
import insta485
from insta485.views.helpers import user_exists


# helper function to get following or follwers
def gen_follow_page(username, follow_type):
    """Display followers of username."""
    # Redirect to login page if not logged in
    if 'logname' not in flask.session:
        return flask.redirect('/accounts/login/')
    logname = flask.session['logname']

    # Connect to database
    connection = insta485.model.get_db()

    # determine if user exists
    if not user_exists(connection, username):
        flask.abort(404)

    if follow_type == "followers":
        # get followers of username
        cur = connection.execute(
            "select u.username, u.filename as user_img_url "
            "from users u "
            "where u.username in "
            "   (select username1 "
            "   from following "
            "   where username2 = ?);",
            (username,)
        )
    elif follow_type == "following":
        # get following of username
        cur = connection.execute(
            "select u.username, u.filename as user_img_url "
            "from users u "
            "where u.username in "
            "   (select username2 "
            "   from following "
            "   where username1 = ?);",
            (username,)
        )
    follow = cur.fetchall()

    # get users that logname follows (for buttons)
    cur = connection.execute(
        "select username2 "
        "from following "
        "where username1 = ?;",
        (logname, )
    )
    query_2_result = cur.fetchall()

    logname_follows = set()
    for user_result in query_2_result:
        logname_follows.add(user_result["username2"])

    for follow_result in follow:
        if follow_result["username"] in logname_follows:
            follow_result["logname_follows_username"] = True
        else:
            follow_result["logname_follows_username"] = False

    context = {"logname": logname, "username": username,
               "follow": follow, "follow_type": follow_type}

    return flask.render_template("follow.html", **context)


@insta485.app.route('/users/<username>/followers/')
def get_followers(username):
    """Show followers page."""
    return gen_follow_page(username, "followers")


@insta485.app.route('/users/<username>/following/')
def get_following(username):
    """Show following page."""
    return gen_follow_page(username, "following")


def post_follow_follow(username):
    """Help other function to follow user."""
    logname = flask.session['logname']

    # Connect to database
    connection = insta485.model.get_db()

    # Check if logname follows username
    cur = connection.execute(
        "select username2 "
        "from following "
        "where username1 = ? and username2 = ?;",
        (logname, username)
    )
    following = cur.fetchall()

    # already following username
    if len(following) == 1:
        flask.abort(409)

    cur = connection.execute(
        "insert into following(username1, username2) "
        "values(?, ?);",
        (logname, username)
    )


def post_follow_unfollow(username):
    """Help other function to unfollow user."""
    logname = flask.session['logname']

    # Connect to database
    connection = insta485.model.get_db()

    # Check if logname follows username
    cur = connection.execute(
        "select username2 "
        "from following "
        "where username1 = ? and username2 = ?;",
        (logname, username)
    )
    following = cur.fetchall()

    # already not following username
    if len(following) == 0:
        flask.abort(409)

    cur = connection.execute(
        "delete from following "
        "where username1 = ? and username2 = ?",
        (logname, username)
    )


@insta485.app.route('/following/', methods=['POST'])
def post_follow():
    """Follow or unfollow user."""
    if 'logname' not in flask.session:
        flask.abort(403)

    redirect_to = flask.request.args.get('target')
    if redirect_to is None:
        redirect_to = "/"

    username = flask.request.form['username']
    action = flask.request.form['operation']
    if action == "follow":
        post_follow_follow(username)
    elif action == "unfollow":
        post_follow_unfollow(username)
    else:
        pass

    return flask.redirect(redirect_to)
