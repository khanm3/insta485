"""REST API for posts."""
import flask
import insta485
from insta485.api.helpers import get_username
from insta485.api.helpers import InvalidUsage


@insta485.app.route('/api/v1/posts/')
def rest_get_posts():
    """Return 10 newest post urls and ids. """
    logname = get_username()
    if not logname:
        raise InvalidUsage("Forbidden", 403)

    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    postid_lte = flask.request.args.get("postid_lte", type=int)
    if size < 0 or page < 0:
        raise InvalidUsage("Bad Request", 400)

    connection = insta485.model.get_db()
    context = {"next": "", "url": flask.request.full_path}
    if context['url'] == "/api/v1/posts/?":
        context['url'] = "/api/v1/posts/"

    # set postid_lte to be the highest post number if not set
    if not postid_lte:
        cur = connection.execute(
            "select postid "
            "from posts "
            "where owner in "
            "   (select username2 "
            "   from following "
            "   where username1 = ? "
            "   union "
            "   select username "
            "   from users "
            "   where users.username = ?) "
            "order by postid desc "
            "limit 1;",
            (logname, logname)
        )
        results = cur.fetchall()
        if len(results) == 0:
            postid_lte = 0
        else:
            postid_lte = results[0]['postid']

    # Get posts
    cur = connection.execute(
        "select postid "
        "from posts "
        "where owner in "
        "   (select username2 "
        "   from following "
        "   where username1 = ? "
        "   union "
        "   select username "
        "   from users "
        "   where users.username = ?) "
        "and postid <= ? "
        "order by postid desc "
        "limit ? "
        "offset ?;",
        (logname, logname, postid_lte, size, size * page)
    )
    results = cur.fetchall()

    if len(results) == size:
        context["next"] = f"/api/v1/posts/?size={size}" +
            f"&page={page + 1}&postid_lte={postid_lte}"

    for post in results:
        post["url"] = f"/api/v1/posts/{post['postid']}/"

    context["results"] = results
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def rest_get_post(postid_url_slug):
    """Return post on postid. """
    logname = get_username()
    if not logname:
        raise InvalidUsage("Forbidden", 403)

    connection = insta485.model.get_db()
    # Get post
    cur = connection.execute(
        "select p.postid, p.filename as imgUrl, p.owner, "
        "p.created, u.filename as ownerImgUrl "
        "from posts p join users u on p.owner = u.username "
        "where p.postid = ?; ",
        (postid_url_slug, )
    )
    post = cur.fetchall()

    if len(post) != 1:
        raise InvalidUsage("Not found", 404)

    # Get comments of this post
    cur = connection.execute(
        "select owner, text, commentid "
        "from comments "
        "where postid = ? "
        "order by commentid asc;",
        (postid_url_slug,)
    )
    comments = cur.fetchall()

    for comment in comments:
        if comment["owner"] == logname:
            comment["lognameOwnsThis"] = True
        else:
            comment["lognameOwnsThis"] = False
        comment["ownerShowUrl"] = f"/users/{comment['owner']}/"
        comment["url"] = f"/api/v1/comments/{comment['commentid']}/"

    # Get likes of this post
    cur = connection.execute(
        "select postid, owner, likeid "
        "from likes "
        "where postid =? ",
        (postid_url_slug, )
    )
    likes = cur.fetchall()

    context_likes = {}
    context_likes["lognameLikesThis"] = False
    context_likes["numLikes"] = len(likes)
    context_likes["url"] = None

    for like in likes:
        if like["owner"] == logname:
            context_likes["lognameLikesThis"] = True
            context_likes["url"] = f"/api/v1/likes/{like['likeid']}/"

    context = {
        "comments": comments,
        "created": post[0]["created"],
        "imgUrl": f"/uploads/{post[0]['imgUrl']}",
        "likes": context_likes,
        "owner": post[0]["owner"],
        "ownerImgUrl": f"/uploads/{post[0]['ownerImgUrl']}",
        "ownerShowUrl": f"/users/{post[0]['owner']}/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": postid_url_slug,
        "url": f"/api/v1/posts/{postid_url_slug}/"
    }

    return flask.jsonify(**context)
