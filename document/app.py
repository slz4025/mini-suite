from flask import Flask, render_template, session, Response, redirect, request
from flask_htmx import HTMX
import sys
from waitress import serve

import src.block as block
import src.command_palette as command_palette
import src.entry as entry
import src.errors as errors
import src.notifications as notifications
import src.settings as settings
import src.wiki as wiki


app = Flask(__name__)
htmx = HTMX(app)
app.config.from_object('config.Config')


def render_null(session):
    return render_template(
            "partials/null.html",
            )


def render_body(session):
    null = render_null(session)
    notification_banner_html = notifications.render(session, False)
    show_command_palette = command_palette.get_show()
    command_palette_html = command_palette.render(session)
    blocks_html = block.render_all(session)
    return render_template(
            "partials/body.html",
            show_command_palette=show_command_palette,
            null=null,
            notification_banner=notification_banner_html,
            command_palette=command_palette_html,
            blocks=blocks_html,
            )


def render(session):
    dark_mode = settings.get_dark_mode()
    body = render_body(session)
    return render_template(
            "index.html",
            dark_mode=dark_mode,
            body=body,
            )

### BEGIN FEEDBACK ###

@app.route("/error")
def unexpected_error():
    error_message = errors.get_message(session)
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


@app.route("/notification/<show>", methods=['PUT'])
@errors.handler
def notification(show):
    assert htmx is not None

    show_notifications = show == "on"
    if not show_notifications:
        notifications.reset()

    return notifications.render(session, show_notifications)

### END FEEDBACK ###


@app.route("/")
@errors.handler
def root():
    entry.use_temp(session)

    return render(session)


### BEGIN SETTINGS ###

@app.route("/dark-mode/<state>", methods=['GET'])
@errors.handler
def dark_mode(state):
    dark_mode = state == "on"
    settings.set_dark_mode(dark_mode)

    return render(session)


@app.route("/command-palette/<state>", methods=['PUT'])
@errors.handler
def command_palette_toggle(state):
    show = state == 'open'
    command_palette.set_show(show)

    return render_body(session)

### END SETTINGS ###


### BEGIN BLOCK ###

@app.route("/block/<id>/focus", methods=['POST'])
@errors.handler
def block_focus(id):
    assert htmx is not None

    prev_in_focus = block.get_in_focus(session)
    block.set_in_focus(session, id)

    html = block.render(session, id)
    resp = Response(html)
    if prev_in_focus is not None:
        # rerender so shows as unfocused
        resp.headers['HX-Trigger'] = f"block-{prev_in_focus}"
    return resp


@app.route("/block/next", methods=['POST'])
@errors.handler
def block_next():
    assert htmx is not None

    block.set_next_in_focus(session)

    return block.render_all(session)


@app.route("/block/prev", methods=['POST'])
@errors.handler
def block_prev():
    assert htmx is not None

    block.set_prev_in_focus(session)

    return block.render_all(session)


@app.route("/block/<id>/edit", methods=['POST'])
@errors.handler
def block_edit(id):
    assert htmx is not None

    contents = request.form["contents"]

    block.set_markdown(contents, id=id)

    return render_null(session)


@app.route("/block/<id>/media", methods=['POST'])
@errors.handler
def block_media(id):
    assert htmx is not None

    file = None
    error = None
    try:
        if 'input' not in request.files:
            raise errors.UserError("File was not chosen.")
        file = request.files['input']
        media_id = entry.save_media(session, file)
        block.append_media_reference(session, id, media_id, alt=file.name)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
    else:
        notifications.set_info("Media appended.")

    html = block.render(session, id)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/block/<id>/up", methods=['PUT'])
@errors.handler
def block_up(id):
    assert htmx is not None

    return block.move_up(session, id)


@app.route("/block/<id>/down", methods=['PUT'])
@errors.handler
def block_down(id):
    assert htmx is not None

    return block.move_down(session, id)


@app.route("/block/<id>/cut", methods=['PUT'])
@errors.handler
def block_cut(id):
    assert htmx is not None

    notifications.set_info("Block copied.")

    html = block.cut(session, id)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/block/<id>/copy", methods=['PUT'])
@errors.handler
def block_copy(id):
    assert htmx is not None

    notifications.set_info("Block copied.")

    html = block.copy(session, id)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/block/<id>/paste", methods=['PUT'])
@errors.handler
def block_paste(id):
    assert htmx is not None

    return block.paste(session, id)


@app.route("/block/<id>/insert", methods=['PUT'])
@errors.handler
def block_insert(id):
    assert htmx is not None

    return block.insert(session, id)


@app.route("/block/<id>/delete", methods=['PUT'])
@errors.handler
def block_delete(id):
    assert htmx is not None

    return block.delete(session, id)


@app.route("/block/<id>", methods=['PUT'])
@errors.handler
def block_endpoint(id):
    assert htmx is not None

    return block.render(session, id=id)

### END BLOCK ###


### BEGIN ENTRY ###

@app.route("/open", methods=['POST'])
@errors.handler
def open_entry():
    assert htmx is not None

    name = request.form["name"]

    error = None
    try:
        entry.check(name)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
        html = render_null(session)
        resp = Response(html)
        resp.headers['HX-Trigger'] = "notification"
        return resp
    else:
        resp = Response()
        resp.headers["HX-Redirect"] = f"/entry/{name}"
        return resp


@app.route("/save", methods=['POST'])
@errors.handler
def save_entry():
    assert htmx is not None

    name = request.form["name"]

    error = None
    try:
        entry.save(session, name)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
    else:
        notifications.set_info("Entry saved.")

    html = render_null(session)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/entry/<name>", methods=['GET'])
@errors.handler
def get_entry(name):
    resp = Response()
    error = None
    try:
        entry.set(session, name)
    except errors.UserError as e:
        error = e

    if error is not None:
        return redirect("/")
    else:
        html = render(session)
        resp.response = html
        return resp


@app.route("/media/<path:filename>", methods=['GET'])
@errors.handler
def get_media(filename):
    return entry.get_media(session, filename)


@app.route("/import", methods=['POST'])
@errors.handler
def import_file():
    assert htmx is not None

    file = None
    error = None
    try:
        if 'input' not in request.files:
            raise errors.UserError("File was not chosen.")
        file = request.files['input']
        entry.import_file(session, file)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
    else:
        notifications.set_info("File imported.")

    html = block.render_all(session)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/export", methods=['POST'])
@errors.handler
def export_file():
    assert htmx is not None

    filename = request.form["input"]

    error = None
    try:
        entry.export(session, filename)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
    else:
        notifications.set_info("File exported.")

    html = render_null(session)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise errors.UserError("Expected just a wiki directory path as input.")
    path = sys.argv[1]

    wiki.set(path)
    notifications.init()
    settings.init()
    command_palette.init()

    serve(app, host='0.0.0.0', port=5000)
