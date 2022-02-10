"""REST API for comments."""
import flask
import insta485
from insta485.api.helpers import get_username
from insta485.api.helpers import InvalidUsage


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def rest_create_comment():
    """Create a new comment."""
    logname = get_username()
    if not logname:
        raise InvalidUsage("Forbidden", 403)

    postid = flask.request.args.get('postid')
    text = flask.request.json['text']
    connection = insta485.model.get_db()

    # determine if post exists
    cur = connection.execute(
        "select postid "
        "from posts "
        "where postid = ?;",
        (postid,)
    )

    if len(cur.fetchall()) < 1:
        raise InvalidUsage("Not found", 404)

    # create comment
    cur = connection.execute(
        "insert into comments(owner, postid, text) "
        "values(?, ?, ?);",
        (logname, postid, text)
    )

    # get commentid
    cur = connection.execute(
        "SELECT last_insert_rowid() as commentid;"
    )
    commentid = cur.fetchall()[0]['commentid']

    # create json return value
    context = {
        "commentid": commentid,
        "lognameOwnsThis": True,
        "owner": logname,
        "ownerShowUrl": f"/users/{logname}/",
        "text": text,
        "url": f"/api/v1/comments/{commentid}/"
    }

    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def rest_delete_comment(commentid):
    """Delete the comment based on the comment id."""
    logname = get_username()
    if not logname:
        raise InvalidUsage("Forbidden", 403)

    conndb = insta485.model.get_db()

    # find comment
    cur = conndb.execute(
        "select owner "
        "from comments "
        "where commentid = ?;",
        (commentid,)
    )

    comment_query = cur.fetchall()
    if len(comment_query) < 1:
        raise InvalidUsage("Not Found", 404)

    comment_owner = comment_query[0]['owner']
    if logname != comment_owner:
        raise InvalidUsage("Forbidden", 403)

    # delete comment
    cur = conndb.execute(
        "delete from comments "
        "where commentid = ?;",
        (commentid,)
    )

    return "", 204
