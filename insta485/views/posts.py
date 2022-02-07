"""
Insta485 index (main) view.

URLs include:
/
"""
import arrow
import flask
import insta485
from insta485.views.helpers import gen_uuid
from insta485.views.helpers import setup_queries
from insta485.views.helpers import delete_img


@insta485.app.route('/posts/<postid>/')
def get_post(postid):
    """Get /posts/<postid> route."""
    # Redirect to login page if not logged in
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('get_account_login'))

    logname, connection = setup_queries()

    # Get post
    cur = connection.execute(
        "select p.postid, p.filename as img_url, p.owner, "
        "p.created as timestamp, u.filename as owner_img_url "
        "from posts p join users u on p.owner = u.username "
        "where p.postid = ?; ",
        (postid, )
    )
    post = cur.fetchall()

    if len(post) != 1:
        flask.abort(404)

    # Get comments of those posts
    cur = connection.execute(
        "select owner, postid, text, commentid "
        "from comments "
        "where postid = ? "
        "order by commentid asc;",
        (postid,)
    )
    comments = cur.fetchall()

    # Get likes of those posts
    cur = connection.execute(
        "select postid, owner "
        "from likes "
        "where postid =? ",
        (postid, )
    )
    likes = cur.fetchall()

    context = {
        "logname": logname,
        "comments": comments,
        "likes": len(likes),
        "liked": False,
        "postid": postid,
        "owner": post[0]["owner"],
        "img_url": post[0]["img_url"],
        "owner_img_url": post[0]["owner_img_url"]
        }

    context["timestamp"] = arrow.get(post[0]["timestamp"],
                                     'YYYY-MM-DD HH:mm:ss').humanize()

    for like in likes:
        if like["owner"] == logname:
            context["liked"] = True

    print(context)
    # Add databse info to context
    return flask.render_template("post.html", **context)


def post_post_create():
    """Create post."""
    logname = flask.session['logname']
    fileobj = flask.request.files['file']

    # Connect to database
    connection = insta485.model.get_db()

    if fileobj:
        uuid_basename = gen_uuid(fileobj)
        connection.execute(
            "insert into posts(filename, owner) "
            "values(?, ?);",
            (uuid_basename, logname)
        )
    else:
        # no file submitted
        flask.abort(400)


def post_post_delete():
    """Delete post."""
    logname = flask.session['logname']
    postid = flask.request.form['postid']

    # Connect to database
    connection = insta485.model.get_db()

    # Check post owner
    cur = connection.execute(
        "select owner "
        "from posts "
        "where postid = ?;",
        (postid, )
    )
    owner = cur.fetchall()

    # Try to delete a post that doesn't exist
    if len(owner) == 0:
        flask.abort(409)

    # Trying to delete a post they don't own
    if owner[0]['owner'] != logname:
        flask.abort(403)

    # Delete post image file
    cur = connection.execute(
        "select filename "
        "from posts "
        "where postid = ?;",
        (postid, )
    )
    result = cur.fetchall()

    delete_img(result[0]['filename'])

    # Delete the post
    cur = connection.execute(
        "delete from posts "
        "where postid = ?;",
        (postid, )
    )


@insta485.app.route('/posts/', methods=['POST'])
def post_post():
    """Post /posts/ create and delete."""
    if 'logname' not in flask.session:
        flask.abort(403)
    logname = flask.session['logname']

    redirect_to = flask.request.args.get('target')
    if redirect_to is None:
        redirect_to = "/users/"+logname+"/"

    action = flask.request.form['operation']
    if action == "create":
        post_post_create()
    elif action == "delete":
        post_post_delete()
    else:
        pass

    return flask.redirect(redirect_to)


@insta485.app.route('/likes/', methods=['POST'])
def post_likes():
    """Like or unlike a post."""
    if 'logname' not in flask.session:
        flask.abort(403)
    logname = flask.session['logname']
    postid = flask.request.form['postid']

    # Connect to database
    connection = insta485.model.get_db()

    # Check if user has previously liked the post
    cur = connection.execute(
        "select * "
        "from likes "
        "where owner = ? and postid = ?;",
        (logname, postid)
    )
    has_liked = len(cur.fetchall()) == 1

    action = flask.request.form['operation']

    if action == "like":
        # User tried to like a post they already liked
        if has_liked:
            flask.abort(409)

        cur = connection.execute(
            "insert into likes(owner, postid) "
            "values(?, ?);",
            (logname, postid)
        )
    elif action == "unlike":
        # User tried to unlike a post they have not liked
        if not has_liked:
            flask.abort(409)

        cur = connection.execute(
            "delete from likes "
            "where owner = ? and postid = ?;",
            (logname, postid)
        )

    redirect_to = flask.request.args.get('target')
    if redirect_to is None:
        redirect_to = "/"

    return flask.redirect(redirect_to)


def create_comment(logname):
    """Create comment on post."""
    text = flask.request.form['text']
    if not text:
        flask.abort(400)

    postid = flask.request.form['postid']
    # do we need to check if len(text) <= 1024 ?
    # do we need to check if post exists?
    connection = insta485.model.get_db()
    connection.execute(
            "insert into comments(owner, postid, text) "
            "values(?, ?, ?);",
            (logname, postid, text)
    )


def delete_comment(logname):
    """Delete comment."""
    commentid = flask.request.form['commentid']
    connection = insta485.model.get_db()
    cur = connection.execute(
            "select * from comments "
            "where commentid = ?;",
            (commentid, )
    )
    comment_entries = cur.fetchall()

    # do we need to check for comment not existing?
    if len(comment_entries) != 1:
        flask.abort(404)
    elif comment_entries[0]['owner'] != logname:
        flask.abort(403)

    connection.execute(
        "delete from comments "
        "where commentid = ?;",
        (commentid, )
    )


@insta485.app.route('/comments/', methods=['POST'])
def post_comments():
    """Create or delete comments on specified post."""
    if 'logname' not in flask.session:
        flask.abort(403)

    logname = flask.session['logname']
    operation = flask.request.form['operation']

    if operation == 'create':
        create_comment(logname)
    elif operation == 'delete':
        delete_comment(logname)

    # invalid operation

    redirect_to = flask.request.args.get('target')
    if not redirect_to:
        redirect_to = "/"

    return flask.redirect(redirect_to)
