from flask import Flask, render_template, session, Response, redirect, request
from flask_htmx import HTMX
import sys
from waitress import serve

import src.block as block
import src.command_palette as command_palette
import src.entry as entry
import src.errors as errors
import src.notifications as notifications
import src.selector as selector
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
    dark_mode = settings.get_dark_mode()
    null = render_null(session)
    notification_banner_html = notifications.render(session)
    show_command_palette = command_palette.get_show()
    command_palette_html = command_palette.render(session)
    current_entry = entry.get(allow_temp=False)
    blocks_html = block.render_all(session)
    return render_template(
            "partials/body.html",
            dark_mode=dark_mode,
            show_command_palette=show_command_palette,
            null=null,
            notification_banner=notification_banner_html,
            command_palette=command_palette_html,
            current_entry=current_entry if current_entry is not None else '',
            blocks=blocks_html,
            )


def render(session):
    body = render_body(session)
    return render_template(
            "index.html",
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

    return notifications.render(session)

### END FEEDBACK ###


@app.route("/")
@errors.handler
def root():
    return redirect("/entry/new")


### BEGIN SETTINGS ###

@app.route("/dark-mode/<state>", methods=['GET'])
@errors.handler
def dark_mode(state):
    dark_mode = state == "on"
    settings.set_dark_mode(dark_mode)

    return render_body(session)


@app.route("/command-palette/<state>", methods=['PUT'])
@errors.handler
def command_palette_toggle(state):
    show = state == 'open'
    command_palette.set_show(show)

    return render_body(session)

### END SETTINGS ###


### BEGIN BLOCK ###

@app.route("/block/unfocus", methods=['POST'])
@errors.handler
def block_unfocus():
    assert htmx is not None

    block.reset_in_focus(session)

    return block.render_all(session)


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


@app.route("/block/<id>/link/<name>", methods=['POST'])
@errors.handler
def block_link(id, name):
    assert htmx is not None

    error = None
    try:
        entry.check(name)
        block.add_link(session, id, name)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
    else:
        notifications.set_info("Link added.")

    html = block.render(session, id)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


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

@app.route("/new", methods=['POST'])
@errors.handler
def new_entry():
    assert htmx is not None

    notifications.set_info("Creating new entry.")
    resp = Response()
    resp.headers["HX-Redirect"] = "/entry/new"
    return resp


@app.route("/open/<name>", methods=['POST'])
@errors.handler
def open_entry(name):
    assert htmx is not None

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
        notifications.set_info("Entry opened.")
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
        html = render_null(session)
        resp = Response(html)
        resp.headers['HX-Trigger'] = "notification"
        return resp
    else:
        resp = Response()
        notifications.set_info("Entry saved.")
        resp.headers["HX-Redirect"] = f"/entry/{name}"
        return resp


@app.route("/entry/<operation>/results", methods=['POST'])
@errors.handler
def get_results(operation):
    assert htmx is not None

    search = request.form["search"]

    return selector.render_results(session, operation, search)


@app.route("/entry/new", methods=['GET'])
@errors.handler
def get_new_entry():
    entry.use_temp(session)

    return render(session)


@app.route("/entry/<name>", methods=['GET'])
@errors.handler
def get_entry(name):
    error = None
    try:
        entry.set(session, name)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
        return redirect("/")
    else:
        return render(session)


@app.route("/media/<path:filename>", methods=['GET'])
@errors.handler
def get_media(filename):
    return entry.get_media(session, filename)


@app.route("/import", methods=['POST'])
@errors.handler
def import_markdown():
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
        notifications.set_info("Markdown imported.")

    html = block.render_all(session)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/export", methods=['POST'])
@errors.handler
def export_html():
    assert htmx is not None

    filename = request.form["input"]

    error = None
    try:
        wiki.export(session, filename)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
    else:
        notifications.set_info("HTML exported.")

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
