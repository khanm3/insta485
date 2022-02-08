"""REST API for likes."""
import flask
import insta485
from insta485.api.helpers import get_username
from insta485.api.helpers import InvalidUsage

@insta485.app.route('/api/v1/likes/', methods=['POST'])
def rest_create_like():
    logname = get_username()
    if not logname:
        raise InvalidUsage("Forbidden", 403)

    connection = insta485.model.get_db()
    postid = flask.request.args.get('postid')

    # determine if like exists
    cur = connection.execute(
            "select likeid "
            "from likes "
            "where owner = ? and postid = ?;",
            (logname, postid)
            )
    result = cur.fetchall()

    # like already exists
    if len(result) == 1:
        likeid = result[0]["likeid"]
        context = {"likeid": likeid, "url": f"/api/v1/likes/{likeid}/"}
        response = flask.jsonify(**context)
        response.status_code = 200
        return response
    # create like and return it
    else:
        connection.execute(
                "insert into likes(owner, postid) "
                "values(?, ?);",
                (logname, postid)
                )
        cur = connection.execute("select last_insert_rowid();")
        likeid = cur.fetchall()[0]['last_insert_rowid()']
        context = {"likeid": likeid, "url": f"/api/v1/likes/{likeid}/"}
        response = flask.jsonify(**context)
        response.status_code = 201
        return response


@insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
def rest_delete_like(likeid):
    logname = get_username()
    if not logname:
        raise InvalidUsage("Forbidden", 403)

    connection = insta485.model.get_db()

    # get user of like
    cur = connection.execute(
            "select owner, postid "
            "from likes "
            "where likeid = ?;",
            (likeid,)
            )
    result = cur.fetchall()
    if len(result) < 1:
        raise InvalidUsage("Not found", 404)
    elif result[0]['owner'] != logname:
        raise InvalidUsage("Forbidden", 403)
    else:
        connection.execute(
            "delete from likes "
            "where likeid = ?;",
            (likeid,)
            )
        return ("", 204)
