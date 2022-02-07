"""
Insta485 index (main) view.

URLs include:
/
"""
from os.path import exists
import arrow
import flask
import insta485
from insta485.views.helpers import setup_queries


@insta485.app.route('/uploads/<filename>')
def get_image(filename):
    """Retrieve an image from the upload folder."""
    if 'logname' not in flask.session:
        flask.abort(403)

    if not exists(insta485.app.config['UPLOAD_FOLDER']/filename):
        flask.abort(404)

    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'], filename, as_attachment=False
    )


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # Redirect to login page if not logged in
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('get_account_login'))

    logname, connection = setup_queries()

    # Get posts of following and self
    cur = connection.execute(
        "select p.postid, p.filename as img_url, p.owner, p.created as "
        "timestamp, u.filename as owner_img_url "
        "from posts p join users u on p.owner = u.username "
        "where p.owner in "
        "   (select username2 "
        "   from following "
        "   where username1 = ? "
        "   union "
        "   select username "
        "   from users "
        "   where users.username = ?) "
        "order by p.postid desc;",
        (logname, logname,)
    )
    posts = cur.fetchall()

    # Get comments of those posts
    cur = connection.execute(
        "select owner, postid, text "
        "from comments "
        "where postid in "
        "   (select p.postid "
        "   from posts p "
        "   where p.owner in "
        "       (select username2 "
        "       from following "
        "       where username1 = ? "
        "       union "
        "       select username "
        "       from users "
        "       where users.username = ?)) "
        "order by commentid asc;",
        (logname, logname)
    )
    comments = cur.fetchall()

    # Get likes of those posts
    cur = connection.execute(
        "select postid, owner "
        "from likes "
        "   where postid in "
        "       (select p.postid "
        "       from posts p "
        "       where p.owner in "
        "           (select username2 "
        "           from following "
        "           where username1 = ? "
        "           union "
        "           select username "
        "           from users "
        "           where users.username = ?)) "
        "order by postid desc;",
        (logname, logname)
    )
    likes = cur.fetchall()

    context = {"logname": logname, "posts": posts}

    for post in context["posts"]:
        post["comments"] = []
        post["likes"] = 0
        post["liked"] = False
        tfmt = 'YYYY-MM-DD HH:mm:ss'
        arrow_obj = arrow.get(post["timestamp"], tfmt)
        post["timestamp"] = arrow_obj.humanize()

        for comment in comments:
            if comment["postid"] == post["postid"]:
                post["comments"].append(comment)

        for like in likes:
            if like["postid"] == post["postid"]:
                post["likes"] = post["likes"] + 1
            if like["owner"] == logname and like["postid"] == post["postid"]:
                post["liked"] = True

    # Add databse info to context
    return flask.render_template("index.html", **context)
