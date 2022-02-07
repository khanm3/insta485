"""Helper functions used in views."""
import hashlib
import os
import pathlib
import uuid
import flask
import insta485


def gen_hash(password, alg='sha512', salt=uuid.uuid4().hex):
    """Return hash of password."""
    # database store: sha512 $ salt $ hash(salt + password)
    print(alg)
    print(salt)
    hash_obj = hashlib.new(alg)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([alg, salt, password_hash])
    return password_db_string


def gen_uuid(fileobj):
    """Return uuid."""
    # rename file
    # Unpack flask object
    filename = fileobj.filename

    # Compute base name (filename without directory).  We use a UUID to avoid
    # clashes with existing files, and ensure that the name is compatible with
    # the filesystem.
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"
    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    return uuid_basename


def user_exists(connection, username):
    """Determine if a user with username exists."""
    cur = connection.execute(
            "select username "
            "from users u "
            "where username = ?;",
            (username,)
            )

    users = cur.fetchall()
    if len(users) > 1:
        assert False
    return len(users) == 1


def setup_queries():
    """Open a database connection and returns it and the logname."""
    return flask.session['logname'], insta485.model.get_db()


def delete_img(filename):
    """Delete file filename from uploads."""
    filepath = insta485.app.config["UPLOAD_FOLDER"]/filename
    os.remove(filepath)


def delete_user_img(logname, connection):
    """Delete the profile pic of logname."""
    cur = connection.execute(
        "select filename "
        "from users "
        "where username = ?;",
        (logname, )
    )
    results = cur.fetchall()

    # If user doesn't exist
    if len(results) != 1:
        flask.abort(404)

    old_filename = results[0]["filename"]
    delete_img(old_filename)
