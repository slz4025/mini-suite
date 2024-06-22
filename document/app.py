from flask import Flask, session, request
from flask_htmx import HTMX
import secrets
from waitress import serve

import src.errors as errors
import src.project as project


app = Flask(__name__)
htmx = HTMX(app)


@app.route("/error")
def unexpected_error():
    error_message = errors.get_message()
    app.logger.error(error_message)

    user_error_msg = f"""
    <p>
        Encountered unexpected error. Please reload.
        Feel free to report the error with the following stack-trace:
    </p>
    <p>
        {error_message}
    </p>
    """
    return user_error_msg


@app.route("/")
@errors.handler
def root():
    return project.root(session)


@app.route("/block/unfocus", methods=['POST'])
@errors.handler
def block_unfocus():
    assert htmx is not None

    return project.block_unfocus(session)


@app.route("/block/<id>/focus", methods=['POST'])
@errors.handler
def block_focus(id):
    assert htmx is not None

    return project.block_focus(session, id)


@app.route("/block/next", methods=['POST'])
@errors.handler
def block_next():
    assert htmx is not None

    return project.block_next(session)


@app.route("/block/prev", methods=['POST'])
@errors.handler
def block_prev():
    assert htmx is not None

    return project.block_prev(session)


@app.route("/block/<id>/edit", methods=['POST'])
@errors.handler
def block_edit(id):
    assert htmx is not None

    contents = request.form["contents"]

    return project.block_edit(session, id, contents)


@app.route("/block/<id>/insert", methods=['PUT'])
@errors.handler
def block_insert(id):
    assert htmx is not None

    return project.block_insert(session, id)


@app.route("/block/<id>/delete", methods=['PUT'])
@errors.handler
def block_delete(id):
    assert htmx is not None

    return project.block_delete(session, id)


@app.route("/block/<id>", methods=['PUT'])
@errors.handler
def block_render(id):
    assert htmx is not None

    return project.block_render(session, id)


@app.route("/save", methods=['POST'])
@errors.handler
def save_entry():
    assert htmx is not None

    return project.save_entry(session)


@app.route("/title/<show_saved_str>", methods=['PUT'])
@errors.handler
def render_title(show_saved_str):
    assert htmx is not None

    show_saved = show_saved_str == "true"

    return project.render_title(session, show_saved=show_saved)


@app.route("/<path:filepath>", methods=['GET'])
@errors.handler
def get_file_obj(filepath):
    return project.get_file_obj(session, filepath)


def start(port, path):
    project.setup(path)
    # key for this session
    app.secret_key = secrets.token_hex()
    app.logger.info("Starting server")
    serve(app, host='0.0.0.0', port=port)
