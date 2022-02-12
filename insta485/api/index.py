"""REST API for index."""
import flask
import insta485


@insta485.app.route('/api/v1/')
def rest_get_index():
    """Return API resource URLs."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context)
