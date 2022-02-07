"""
Users view.

URLs include:
/users/<username>/
"""
import flask
import insta485
from insta485.views.helpers import setup_queries


@insta485.app.route('/users/<username>/')
def get_user(username):
    """Display user page for specified username."""
    # Redirect to login page if logged in
    if 'logname' not in flask.session:
        return flask.redirect("/accounts/login/")

    logname, connection = setup_queries()

    # make sure user exists
    cur = connection.execute(
        "select fullname "
        "from users u "
        "where u.username = ?;",
        (username,)
    )
    fullname = cur.fetchall()

    if len(fullname) != 1:
        flask.abort(404)

    context = {"logname": logname, "username": username,
               "logname_follows_username": False,
               "fullname": fullname[0]['fullname']}

    # get relationship
    cur = connection.execute(
        "select username1 "
        "from following "
        "where username1 = ? and username2 = ?;",
        (logname, username)
    )
    relation = cur.fetchall()
    if len(relation) == 1:
        context["logname_follows_username"] = True

    # get post images from user
    cur = connection.execute(
        "select postid, filename as img_url "
        "from posts "
        "where owner = ?;",
        (username,)
    )
    posts = cur.fetchall()
    context["total_posts"] = len(posts)
    context["posts"] = posts

    # get users number of followers
    cur = connection.execute(
        "select username1 "
        "from following "
        "where username2 = ?;",
        (username,)
    )
    followers = cur.fetchall()
    context["followers"] = len(followers)

    # get users number of following
    cur = connection.execute(
        "select username1 "
        "from following "
        "where username1 = ?;",
        (username,)
    )
    following = cur.fetchall()
    context["following"] = len(following)

    return flask.render_template("user.html", **context)
