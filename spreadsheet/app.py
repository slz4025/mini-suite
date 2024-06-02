from flask import (
    Flask,
    request,
    session,
)
from flask_htmx import HTMX
import secrets
from waitress import serve

import src.errors as errors
from src.session import Session
import src.selector.types as sel_types


app = Flask(__name__)
htmx = HTMX(app)
_session = None


@app.route("/error")
def render_error():
    return _session.render_error(app.logger)


@app.route("/")
@errors.handler
def root():
    assert htmx is not None

    return _session.root(session)


@app.route("/command-palette/toggle", methods=['PUT'])
@errors.handler
def toggle_command_palette():
    assert htmx is not None

    return _session.toggle_command_palette(session)


@app.route("/save", methods=['POST'])
@errors.handler
def save():
    assert htmx is not None

    return _session.save(session)


@app.route("/help/toggle", methods=['PUT'])
@errors.handler
def toggle_help():
    assert htmx is not None

    return _session.toggle_help(session)


@app.route("/port", methods=['PUT'])
@errors.handler
def render_port():
    assert htmx is not None

    return _session.render_port(session)


@app.route("/cell/<row>/<col>", methods=['PUT'])
@errors.handler
def render_cell(row, col):
    assert htmx is not None

    cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(int(row)),
        col_index=sel_types.ColIndex(int(col)),
    )
    return _session.render_cell(session, cell_position)


@app.route("/cell/<row>/<col>/focus", methods=['POST'])
@errors.handler
def focus_cell(row, col):
    assert htmx is not None

    cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(int(row)),
        col_index=sel_types.ColIndex(int(col)),
    )

    return _session.focus_cell(session, cell_position)


@app.route("/cell/<row>/<col>/update", methods=['POST'])
@errors.handler
def update_cell(row, col):
    assert htmx is not None

    cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(int(row)),
        col_index=sel_types.ColIndex(int(col)),
    )

    key = f"input-cell-{row}-{col}"
    value = request.form[key]

    return _session.update_cell(session, cell_position, value)


@app.route("/cell/<row>/<col>/sync", methods=['POST'])
@errors.handler
def sync_cell(row, col):
    assert htmx is not None

    cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(int(row)),
        col_index=sel_types.ColIndex(int(col)),
    )

    key = f"input-cell-{row}-{col}"
    if key not in request.form:
        return
    value = request.form[key]

    return _session.sync_cell(session, cell_position, value)


@app.route("/editor/toggle", methods=['PUT'])
@errors.handler
def toggle_editor():
    assert htmx is not None

    return _session.toggle_editor(session)


@app.route("/editor/operations", methods=['PUT'])
@errors.handler
def render_editor_operations():
    assert htmx is not None

    return _session.render_editor_operations(session)


@app.route("/editor/operation/<op_name_str>", methods=['PUT'])
@errors.handler
def preview_editor_operation(op_name_str):
    assert htmx is not None

    return _session.preview_editor_operation(session, op_name_str)


@app.route("/editor", methods=['PUT'])
@errors.handler
def render_editor():
    assert htmx is not None

    return _session.render_editor(session)


@app.route("/selector/toggle", methods=['PUT'])
@errors.handler
def toggle_selector():
    assert htmx is not None

    return _session.toggle_selector(session)


# Though this updates the shown selector form,
# we use 'GET' in order to retrieve the request argument.
@app.route("/selector/input", methods=['GET'])
@errors.handler
def render_selector_input():
    assert htmx is not None

    mode_str = request.args["mode"]

    return _session.render_selector_input(session, mode_str)


@app.route(
    "/selector/start/<start_row>/<start_col>/end/<end_row>/<end_col>",
    methods=['POST'],
)
@errors.handler
def update_selection_from_endpoints(start_row, start_col, end_row, end_col):
    assert htmx is not None

    start = sel_types.CellPosition(
        row_index=sel_types.RowIndex(int(start_row)),
        col_index=sel_types.ColIndex(int(start_col)),
    )
    end = sel_types.CellPosition(
        row_index=sel_types.RowIndex(int(end_row)),
        col_index=sel_types.ColIndex(int(end_col)),
    )

    return _session.update_selection_from_endpoints(session, start, end) 


@app.route("/selector/move/<direction>", methods=['POST'])
@errors.handler
def move_selection(direction):
    assert htmx is not None

    return _session.move_selection(session, direction)


@app.route("/selector", methods=['POST'])
@errors.handler
def update_selection():
    assert htmx is not None

    form = request.form

    return _session.update_selection(session, form)


@app.route("/selector", methods=['DELETE'])
def delete_selection():
    assert htmx is not None

    return _session.delete_selection(session)


@app.route("/bulk-editor/toggle", methods=['PUT'])
@errors.handler
def toggle_bulk_editor():
    assert htmx is not None

    return _session.toggle_bulk_editor(session)


# Though this updates the shown operation form,
# we use 'GET' in order to retrieve the request argument.
@app.route("/bulk-editor/operation", methods=['GET'])
@errors.handler
def render_bulk_editor_operation():
    assert htmx is not None

    name_str = request.args["operation"]

    return _session.render_bulk_editor_operation(session, name_str)


@app.route("/bulk-editor/apply/<name_str>", methods=['POST'])
@errors.handler
def apply_bulk_editor_operation(name_str):
    assert htmx is not None

    return _session.apply_bulk_editor_operation(session, name_str)


@app.route("/bulk-editor", methods=['PUT'])
@errors.handler
def render_bulk_editor():
    assert htmx is not None

    return _session.render_bulk_editor(session)


@app.route("/bulk-editor", methods=['POST'])
@errors.handler
def apply_bulk_edit():
    assert htmx is not None

    form = request.form

    return _session.apply_bulk_edit(session, form)


@app.route("/notification/<show>", methods=['PUT'])
@errors.handler
def render_notification(show):
    assert htmx is not None

    return _session.render_notification(session, show)


@app.route("/viewer/toggle", methods=['PUT'])
@errors.handler
def toggle_viewer():
    assert htmx is not None

    return _session.toggle_viewer(session)


@app.route("/viewer/target", methods=['PUT'])
@errors.handler
def render_cell_targeter():
    assert htmx is not None

    return _session.render_cell_targeter(session)


@app.route("/viewer/target", methods=['POST'])
@errors.handler
def apply_cell_target():
    assert htmx is not None

    return _session.apply_cell_target(session)


@app.route("/viewer/move/<method>", methods=['POST'])
@errors.handler
def move_port(method):
    assert htmx is not None

    return _session.move_port(session, method)


@app.route("/viewer/dimensions", methods=['POST'])
@errors.handler
def update_dimensions():
    assert htmx is not None

    nrows = int(request.form['nrows'])
    ncols = int(request.form['ncols'])

    return _session.update_dimensions(session, nrows, ncols)


def start(port, path, debug):
    global _session
    _session = Session(path, debug)
    # key for this session
    app.secret_key = secrets.token_hex()
    app.logger.info("Starting server")
    serve(app, host='0.0.0.0', port=port)
