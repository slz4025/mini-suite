from flask import Flask, session, request, redirect
from flask_htmx import HTMX
from waitress import serve

import src.errors as errors
import src.project as project


app = Flask(__name__)
htmx = HTMX(app)
app.config.from_object('config.Config')


def get_file(files):
    if 'input' not in files:
        raise errors.UserError("File was not chosen.")
    file = request.files['input']
    return file


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

    return project.notification(session, show)


@app.route("/")
@errors.handler
def root():
    return redirect("/entry/temp")


@app.route("/dark-mode/<state>", methods=['GET'])
@errors.handler
def dark_mode(state):
    assert htmx is not None

    return project.dark_mode(session, state)


@app.route("/command-palette/io/<operation>", methods=['PUT'])
@errors.handler
def command_palette_operation(operation):
    assert htmx is not None

    return project.command_palette_operation(session, operation)


@app.route("/command-palette/<state>", methods=['PUT'])
@errors.handler
def command_palette_toggle(state):
    assert htmx is not None

    return project.command_palette_toggle(session, state)


@app.route("/block/infocus", methods=['GET'])
@errors.handler
def get_block_in_focus():
    id = project.get_block_in_focus(session)
    if id is None:
        return {}
    else:
        return {"id": id}


@app.route("/block/<id>/inputs/<operation>", methods=['PUT'])
@errors.handler
def block_operation(id, operation):
    assert htmx is not None

    return project.block_operation(session, id, operation)


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


@app.route("/block/<id>/link/<name>", methods=['POST'])
@errors.handler
def block_link(id, name):
    assert htmx is not None

    return project.block_link(session, id, name)


@app.route("/block/<id>/media", methods=['POST'])
@errors.handler
def block_media(id):
    assert htmx is not None

    file = get_file(request.files)
    return project.block_media(session, id, file)


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


@app.route("/new", methods=['POST'])
@errors.handler
def new_entry():
    assert htmx is not None

    return project.new_entry(session)


@app.route("/open/<name>", methods=['POST'])
@errors.handler
def open_entry(name):
    assert htmx is not None

    return project.open_entry(session, name)


@app.route("/save", methods=['POST'])
@errors.handler
def save_entry():
    assert htmx is not None

    name = request.form["name"]

    return project.save_entry(session, name)


@app.route("/entry/<operation>/results", methods=['POST'])
@errors.handler
def get_entry_results(operation):
    assert htmx is not None

    search = request.form["search"]

    return project.get_entry_results(session, operation, search)


@app.route("/entry/temp", methods=['GET'])
@errors.handler
def get_temp_entry():
    return project.get_temp_entry(session)


@app.route("/entry/<name>", methods=['GET'])
@errors.handler
def get_wiki_entry(name):
    return project.get_wiki_entry(session, name)


@app.route("/media/<path:filename>", methods=['GET'])
@errors.handler
def get_media(filename):
    return project.get_media(session, filename)


@app.route("/import", methods=['POST'])
@errors.handler
def import_markdown():
    assert htmx is not None

    file = get_file(request.files)

    return project.import_markdown(session, file)


@app.route("/export", methods=['POST'])
@errors.handler
def export_html():
    assert htmx is not None

    filename = request.form["input"]
    return project.export_html(session, filename)


def start(port, wiki_path, one_off_file=None):
    project.setup(wiki_path, one_off_file)

    print(f"Serving on port {port}.")
    serve(app, host='0.0.0.0', port=port)
