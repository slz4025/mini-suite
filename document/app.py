from flask import Flask, redirect, request, Response, send_from_directory
from flask_htmx import HTMX
import os
from waitress import serve

from settings import Settings

import src.errors as errors
from src.state import get_init_entry_id, get_entry


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
    entry_id = get_init_entry_id()
    return redirect(f"/entry/{entry_id}")


@app.route("/entry/<entry_id>")
@errors.handler
def render_entry(entry_id):
    resp = Response()

    entry = get_entry(entry_id)

    dark_mode = Settings.DARK_MODE
    entry_html = entry.render(dark_mode)
    resp.set_data(entry_html)
    return resp


@app.route("/entry/<entry_id>/block/<block_id>", methods=['PUT'])
@errors.handler
def render_block(entry_id, block_id):
    assert htmx is not None

    resp = Response()

    entry = get_entry(entry_id)

    block_html = entry.render_block(block_id)
    resp.set_data(block_html)
    return resp


@app.route("/entry/<entry_id>/block/focus/<block_id>", methods=['POST'])
@errors.handler
def focus_block(entry_id, block_id):
    assert htmx is not None

    resp = Response()

    entry = get_entry(entry_id)

    prev_block_id = entry.get_in_focus()
    entry.set_in_focus(block_id)

    if prev_block_id is not None:
        # rerender so shows as unfocused
        resp.headers['HX-Trigger'] = f"block-{prev_block_id}"

    block_html = entry.render_block(block_id)
    resp.set_data(block_html)
    return resp


@app.route("/entry/<entry_id>/block/unfocus", methods=['POST'])
@errors.handler
def unfocus_block(entry_id):
    assert htmx is not None

    resp = Response()

    entry = get_entry(entry_id)

    block_id = entry.unfocus_block()

    block_html = entry.render_block(block_id)
    resp.set_data(block_html)
    return resp


@app.route("/entry/<entry_id>/block/next", methods=['POST'])
@errors.handler
def next_block(entry_id):
    assert htmx is not None

    resp = Response()

    entry = get_entry(entry_id)

    curr_block_id = entry.get_in_focus()
    next_block_id = entry.focus_next_block()

    if next_block_id != curr_block_id:
        resp.headers['HX-Trigger'] = f"block-{next_block_id}"

    block_html = entry.render_block(curr_block_id)
    resp.set_data(block_html)
    return resp


@app.route("/entry/<entry_id>/block/prev", methods=['POST'])
@errors.handler
def prev_block(entry_id):
    assert htmx is not None

    resp = Response()

    entry = get_entry(entry_id)

    curr_block_id = entry.get_in_focus()
    next_block_id = entry.focus_prev_block()

    if next_block_id != curr_block_id:
        resp.headers['HX-Trigger'] = f"block-{next_block_id}"

    block_html = entry.render_block(curr_block_id)
    resp.set_data(block_html)
    return resp


@app.route("/entry/<entry_id>/block/edit", methods=['POST'])
@errors.handler
def edit_block(entry_id):
    assert htmx is not None

    contents = request.form["contents"]

    resp = Response()

    entry = get_entry(entry_id)

    entry.edit_block(contents)

    null_html = entry.render_null()
    resp.set_data(null_html)
    return resp


@app.route("/entry/<entry_id>/block/insert", methods=['PUT'])
@errors.handler
def insert_block(entry_id):
    assert htmx is not None

    resp = Response()

    entry = get_entry(entry_id)

    curr_id = entry.get_in_focus()
    new_id = entry.insert_block()
    curr_block = entry.render_block(curr_id)
    next_block = entry.render_block(new_id)
    blocks_html = "\n".join([curr_block, next_block])

    resp.set_data(blocks_html)
    return resp


@app.route("/entry/<entry_id>/block/delete", methods=['PUT'])
@errors.handler
def delete_block(entry_id):
    assert htmx is not None

    resp = Response()

    entry = get_entry(entry_id)

    entry.delete_block()

    curr_id = entry.get_in_focus()
    if curr_id is not None:
        resp.headers['HX-Trigger'] = f"block-{curr_id}"

    blocks_html = ""
    resp.set_data(blocks_html)
    return resp


@app.route("/entry/<entry_id>/save", methods=['POST'])
@errors.handler
def save(entry_id):
    assert htmx is not None

    resp = Response()

    entry = get_entry(entry_id)

    entry.save()

    banner_html = entry.render_banner(show_saved=True)
    resp.set_data(banner_html)
    return resp


@app.route("/entry/<entry_id>/banner/reset", methods=['PUT'])
@errors.handler
def reset_banner(entry_id):
    assert htmx is not None

    resp = Response()

    entry = get_entry(entry_id)

    banner_html = entry.render_banner(show_saved=False)
    resp.set_data(banner_html)
    return resp


@app.route("/<path:filepath>", methods=['GET'])
@errors.handler
def get_file_obj(filepath):
    filepath = "/" + filepath
    filedir, filename = os.path.split(filepath)
    return send_from_directory(filedir, filename)


def start(port):
    app.logger.info("Starting server")
    serve(app, host='0.0.0.0', port=port)
