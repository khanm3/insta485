"""
Explore view.

URLs include:
/explore/
"""
import flask
import insta485
from insta485.views.helpers import setup_queries


@insta485.app.route('/explore/')
def get_explore():
    """Get /explore/ route."""
    # Redirect to login page if not logged in
    if 'logname' not in flask.session:
        return flask.redirect("/accounts/login/")

    logname, connection = setup_queries()

    # Get users who logname doesn't follow
    cur = connection.execute(
        "select u.username, u.filename as user_img_url "
        "from users u "
        "where u.username not in "
        "   (select f.username2 "
        "   from following f "
        "   where f.username1 = ? "
        "   union "
        "   select username "
        "   from users "
        "   where username = ?);",
        (logname, logname)
    )
    users = cur.fetchall()

    context = {"logname": logname, "not_following": users}

    return flask.render_template("explore.html", **context)
