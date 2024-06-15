from flask import (
    Flask,
    request,
)
from flask_htmx import HTMX
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

    return _session.root()


@app.route("/notification/<show>", methods=['PUT'])
@errors.handler
def render_notification(show):
    assert htmx is not None

    return _session.render_notification(show)


@app.route("/command-palette/toggle", methods=['PUT'])
@errors.handler
def toggle_command_palette():
    assert htmx is not None

    return _session.toggle_command_palette()


@app.route("/save", methods=['POST'])
@errors.handler
def save():
    assert htmx is not None

    return _session.save()


@app.route("/help/toggle", methods=['PUT'])
@errors.handler
def toggle_help():
    assert htmx is not None

    return _session.toggle_help()


@app.route("/port", methods=['PUT'])
@errors.handler
def render_port():
    assert htmx is not None

    return _session.render_port()


@app.route("/cell/<row>/<col>", methods=['PUT'])
@errors.handler
def render_cell(row, col):
    assert htmx is not None

    cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(int(row)),
        col_index=sel_types.ColIndex(int(col)),
    )
    return _session.render_cell(cell_position)


@app.route("/cell/<row>/<col>/focus", methods=['POST'])
@errors.handler
def focus_cell(row, col):
    assert htmx is not None

    cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(int(row)),
        col_index=sel_types.ColIndex(int(col)),
    )

    return _session.focus_cell(cell_position)


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

    return _session.update_cell(cell_position, value)


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

    return _session.sync_cell(cell_position, value)


@app.route("/selector/toggle", methods=['PUT'])
@errors.handler
def toggle_selector():
    assert htmx is not None

    return _session.toggle_selector()


# Though this updates the shown selector form,
# we use 'GET' in order to retrieve the request argument.
@app.route("/selector/input", methods=['GET'])
@errors.handler
def use_selector_input():
    assert htmx is not None

    mode_str = request.args["mode"]

    return _session.use_selector_input(mode_str)


@app.route("/selector/search/text", methods=['POST'])
@errors.handler
def update_search_results():
    assert htmx is not None

    text = request.form["text-search"]

    return _session.update_search_results(text) 


@app.route(
    "/selector/search/cell-position/<row>/<col>",
    methods=['POST'],
)
@errors.handler
def update_selector_cell_position(row, col):
    assert htmx is not None

    pos = sel_types.CellPosition(
        row_index=sel_types.RowIndex(int(row)),
        col_index=sel_types.ColIndex(int(col)),
    )

    return _session.update_selector_cell_position(pos) 


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

    return _session.update_selection_from_endpoints(start, end) 


@app.route("/selector/move/<direction>", methods=['POST'])
@errors.handler
def move_selection(direction):
    assert htmx is not None

    return _session.move_selection(direction)


@app.route("/selector", methods=['POST'])
@errors.handler
def update_selection():
    assert htmx is not None

    form = request.form

    return _session.update_selection(form)


@app.route("/selector", methods=['DELETE'])
def delete_selection():
    assert htmx is not None

    return _session.delete_selection()


@app.route("/editor/toggle", methods=['PUT'])
@errors.handler
def toggle_editor():
    assert htmx is not None

    return _session.toggle_editor()


@app.route("/editor/operations", methods=['PUT'])
@errors.handler
def render_editor_operations():
    assert htmx is not None

    return _session.render_editor_operations()


@app.route("/editor/operation/<op_name_str>", methods=['PUT'])
@errors.handler
def preview_editor_operation(op_name_str):
    assert htmx is not None

    return _session.preview_editor_operation(op_name_str)


@app.route("/editor", methods=['PUT'])
@errors.handler
def render_editor():
    assert htmx is not None

    return _session.render_editor()


@app.route("/bulk-editor/toggle", methods=['PUT'])
@errors.handler
def toggle_bulk_editor():
    assert htmx is not None

    return _session.toggle_bulk_editor()


# Though this updates the shown operation form and underlying state,
# we use 'GET' in order to retrieve the request argument.
@app.route("/bulk-editor/operation", methods=['GET'])
@errors.handler
def use_bulk_editor_operation():
    assert htmx is not None

    name_str = request.args["operation"]

    return _session.use_bulk_editor_operation(name_str)


# Bulk-editor operations that only require at most a default selection.
@app.route("/bulk-editor/apply/<name_str>", methods=['POST'])
@errors.handler
def apply_bulk_editor_operation(name_str):
    assert htmx is not None

    return _session.apply_bulk_editor_operation(name_str)


@app.route("/bulk-editor/use-selection/<op>/<use>", methods=['PUT'])
@errors.handler
def render_bulk_editor_use_selection(op, use):
    assert htmx is not None

    return _session.render_bulk_editor_use_selection(op, use)


@app.route("/bulk-editor/use-selection/<op_name>/<use>", methods=['POST'])
@errors.handler
def add_bulk_editor_selection(op_name, use):
    assert htmx is not None

    return _session.add_bulk_editor_selection(op_name, use)


@app.route("/bulk-editor", methods=['PUT'])
@errors.handler
def render_bulk_editor():
    assert htmx is not None

    return _session.render_bulk_editor()


@app.route("/bulk-editor", methods=['POST'])
@errors.handler
def apply_bulk_edit():
    assert htmx is not None

    form = request.form

    return _session.apply_bulk_edit(form)


@app.route("/viewer/toggle", methods=['PUT'])
@errors.handler
def toggle_viewer():
    assert htmx is not None

    return _session.toggle_viewer()


@app.route("/viewer/target", methods=['PUT'])
@errors.handler
def render_cell_targeter():
    assert htmx is not None

    return _session.render_cell_targeter()


@app.route("/viewer/target", methods=['POST'])
@errors.handler
def apply_target():
    assert htmx is not None

    return _session.apply_target()


@app.route("/viewer/move/<method>", methods=['POST'])
@errors.handler
def move_port(method):
    assert htmx is not None

    return _session.move_port(method)


@app.route("/viewer/dimensions", methods=['POST'])
@errors.handler
def update_dimensions():
    assert htmx is not None

    nrows = int(request.form['nrows'])
    ncols = int(request.form['ncols'])

    return _session.update_dimensions(nrows, ncols)


def start(port, path, debug):
    global _session
    _session = Session(path, debug)
    app.logger.info("Starting server")
    serve(app, host='0.0.0.0', port=port)
