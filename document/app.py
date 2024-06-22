from flask import Flask, request
from flask_htmx import HTMX
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
    return project.root()


@app.route("/block/unfocus", methods=['POST'])
@errors.handler
def block_unfocus():
    assert htmx is not None

    return project.block_unfocus()


@app.route("/block/<id>/focus", methods=['POST'])
@errors.handler
def block_focus(id):
    assert htmx is not None

    return project.block_focus(id)


@app.route("/block/next", methods=['POST'])
@errors.handler
def block_next():
    assert htmx is not None

    return project.block_next()


@app.route("/block/prev", methods=['POST'])
@errors.handler
def block_prev():
    assert htmx is not None

    return project.block_prev()


@app.route("/block/<id>/edit", methods=['POST'])
@errors.handler
def block_edit(id):
    assert htmx is not None

    contents = request.form["contents"]

    return project.block_edit(id, contents)


@app.route("/block/<id>/insert", methods=['PUT'])
@errors.handler
def block_insert(id):
    assert htmx is not None

    return project.block_insert(id)


@app.route("/block/<id>/delete", methods=['PUT'])
@errors.handler
def block_delete(id):
    assert htmx is not None

    return project.block_delete(id)


@app.route("/block/<id>", methods=['PUT'])
@errors.handler
def block_render(id):
    assert htmx is not None

    return project.block_render(id)


@app.route("/save", methods=['POST'])
@errors.handler
def save():
    assert htmx is not None

    return project.save()


@app.route("/banner/reset", methods=['PUT'])
@errors.handler
def reset_banner():
    assert htmx is not None

    return project.render_banner(show_saved=False)


@app.route("/<path:filepath>", methods=['GET'])
@errors.handler
def get_file_obj(filepath):
    return project.get_file_obj(filepath)


def start(port, path):
    project.setup(path)
    app.logger.info("Starting server")
    serve(app, host='0.0.0.0', port=port)
