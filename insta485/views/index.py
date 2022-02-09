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

    logname = flask.session.get('logname')
    context = {"logname": logname}

    # Add databse info to context
    return flask.render_template("index.html", **context)
