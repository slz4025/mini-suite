from flask import (
    Flask,
    render_template,
    session,
    request,
    Response,
)
from flask_htmx import HTMX
from waitress import serve

import src.bulk_editor as bulk_editor
import src.command_palette as command_palette
import src.editor as editor
import src.errors as errors
import src.files as files
import src.navigator as navigator
import src.notifications as notifications
import src.port as port
import src.selection as selection
import src.settings as settings

import src.data.sheet as sheet
import src.data.computer as computer
import src.data.operations as operations

app = Flask(__name__)
htmx = HTMX(app)
app.config.from_object('config.Config')


# Populate with fake data.
DEBUG = True


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


def render_null(session):
    return render_template("partials/null.html")


def render_body(session):
    null = render_null(session)
    notification_banner = notifications.render(session, False)
    show_command_palette = command_palette.get_show(session)
    command_palette_html = command_palette.render(session)
    port_html = port.render(session)
    body = render_template(
            "partials/body.html",
            null=null,
            notification_banner=notification_banner,
            command_palette=command_palette_html,
            data=port_html,
            show_command_palette=show_command_palette,
            )
    return body


@app.route("/")
@errors.handler
def root():
    assert htmx is not None

    # TODO: This should eventually be done for the user for the sheet.
    command_palette.init(session)
    notifications.init(session)
    navigator.init(session)

    # TODO: This should eventually be done for the user
    # or for the user for the sheet.
    settings.init(session)

    # TODO: This should eventually be done only on the creation of the sheet.
    sheet.init(DEBUG)

    body = render_body(session)
    return render_template(
        "index.html",
        data=body,
        )


@app.route("/data", methods=['GET'])
@errors.handler
def data():
    assert htmx is not None

    dump = sheet.get_dump()

    return dump


@app.route("/command-palette/toggle", methods=['PUT'])
@errors.handler
def command_palette_toggle():
    assert htmx is not None

    show_command_palette = command_palette.get_show(session)
    command_palette.set_show(session, not show_command_palette)

    return render_body(session)


@app.route("/help/toggle", methods=['PUT'])
@errors.handler
def help_toggler():
    assert htmx is not None

    show_help = command_palette.get_show_help(session)
    command_palette.set_show_help(session, not show_help)

    return command_palette.render(session)


@app.route("/port", methods=['PUT'])
@errors.handler
def update_port():
    assert htmx is not None

    port_html = port.render(session)
    resp = Response(port_html)
    resp.headers['HX-Trigger'] = "editor"
    return resp


@app.route("/cell/<row>/<col>", methods=['PUT'])
@errors.handler
def cell_render(row, col):
    assert htmx is not None

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )

    return port.render_cell(session, cell_position)


@app.route("/cell/<row>/<col>/update", methods=['PUT'])
@errors.handler
def cell_rerender(row, col):
    assert htmx is not None

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )

    key = f"input-cell-{row}-{col}"
    value = request.form[key]

    error = None
    try:
        operations.update_cell(cell_position, value)
    except (errors.UserError) as e:
        error = e

    if error is not None:
        notifications.set_error(session, error)
    else:
        notifications.set_info(session, "Updated cell value successfully.")

    # Re-render the entire port in case other cells depended on the
    # current cell's value.
    port_html = port.render(session)
    resp = Response(port_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/cell/<row>/<col>/focus", methods=['PUT'])
@errors.handler
def cell_focus(row, col):
    assert htmx is not None

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )

    prev_focused = editor.get_focused_cell_position(session)
    editor.set_focused_cell_position(session, cell_position)

    editor_html = editor.render(session)
    resp = Response(editor_html)

    if cell_position != prev_focused:
        # change highlight
        resp.headers['HX-Trigger'] = f"cell-{row}-{col},cell"\
            + f"-{prev_focused.row_index.value}"\
            + f"-{prev_focused.col_index.value}"

    return resp


# Update cell value from within cell.
def update_cell(cell_position):
    error = None

    row = cell_position.row_index.value
    col = cell_position.col_index.value
    key = f"input-cell-{row}-{col}"

    if key not in request.form:
        return None

    value = request.form[key]
    prev_value = operations.get_cell_formula(cell_position)

    if computer.is_formula(prev_value):
        error = errors.UserError(
            "About to override underlying formula. "
            "Use the editor to view the formula "
            "and update the value instead."
        )
        notifications.set_error(session, error)
    elif computer.is_formula(value):
        error = errors.UserError(
            "Cannot input a formula in the cell. Use the editor instead."
        )
        notifications.set_error(session, error)
    else:
        operations.update_cell(cell_position, value)

    return error


@app.route("/cell/<row>/<col>/sync", methods=['PUT'])
@errors.handler
def cell_sync(row, col):
    assert htmx is not None

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )

    error = update_cell(cell_position)

    editor_html = editor.render(session)
    resp = Response(editor_html)
    if error is not None:
        resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/editor/toggle", methods=['PUT'])
@errors.handler
def editor_toggler():
    assert htmx is not None

    show_editor = command_palette.get_show_editor(session)
    command_palette.set_show_editor(session, not show_editor)

    html = editor.render(session)
    return html


@app.route("/editor", methods=['PUT'])
@errors.handler
def editor_endpoint():
    assert htmx is not None

    html = editor.render(session)
    resp = Response(html)
    return resp


@app.route("/selection/toggle", methods=['PUT'])
@errors.handler
def selection_toggler():
    assert htmx is not None

    show_selection = command_palette.get_show_selection(session)
    command_palette.set_show_selection(session, not show_selection)

    html = selection.render(session)
    return html


# Though this updates the shown selection form,
# we use 'GET' in order to retrieve the request argument.
@app.route("/selection/inputs", methods=['GET'])
@errors.handler
def selection_inputs():
    assert htmx is not None

    mode_str = request.args["mode"]
    mode = selection.modes.from_input(mode_str)
    return selection.render_inputs(session, mode)


def update_selection(mode, sel, error, reset=False):
    resp = Response()
    resp.headers['HX-Trigger'] = "notification"

    if error is not None:
        notifications.set_error(session, error)
    else:
        if reset:
            selection.reset(session)
        else:
            selection.save(session, mode, sel)

        notifications.set_info(session, "Selection {}.".format(
            "cleared" if reset else "registered"
        ))
        # Rerender what operations are allowed based on selection.
        resp.headers['HX-Trigger'] += ",bulk-editor"
        # Show selection in port.
        resp.headers['HX-Trigger'] += ",update-port"
        # Update showing navigator target feature.
        resp.headers['HX-Trigger'] += ",navigator-target"

    return resp


@app.route(
    "/selection/start/<start_row>/<start_col>/end/<end_row>/<end_col>",
    methods=['PUT'],
)
@errors.handler
def selection_end(start_row, start_col, end_row, end_col):
    assert htmx is not None

    start = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(start_row)),
        col_index=selection.types.ColIndex(int(start_col)),
    )
    end = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(end_row)),
        col_index=selection.types.ColIndex(int(end_col)),
    )

    mode = None
    sel = None
    error = None
    try:
        mode, sel = selection.compute_from_endpoints(start, end)
    except (errors.NotSupportedError) as e:
        error = e

    resp = update_selection(mode, sel, error)
    html = selection.render(session)
    resp.response = html
    return resp


@app.route("/selection", methods=['POST', 'DELETE'])
@errors.handler
def selection_endpoint():
    assert htmx is not None

    mode = None
    sel = None
    error = None
    match request.method:
        case 'POST':
            reset = False
            try:
                mode, sel = selection.validate_and_parse(session, request.form)
            except (errors.UserError, errors.OutOfBoundsError) as e:
                error = e
        case 'DELETE':
            reset = True

    resp = update_selection(mode, sel, error, reset=reset)
    html = selection.render(session)
    resp.response = html
    return resp


@app.route("/bulk-editor/toggle", methods=['PUT'])
@errors.handler
def bulk_editor_toggler():
    assert htmx is not None

    show_bulk_editor = command_palette.get_show_bulk_editor(session)
    command_palette.set_show_bulk_editor(session, not show_bulk_editor)

    html = bulk_editor.render(session)
    return html


# Though this updates the shown operation form,
# we use 'GET' in order to retrieve the request argument.
@app.route("/bulk-editor/operation", methods=['GET'])
@errors.handler
def bulk_editor_operation():
    assert htmx is not None

    name_str = request.args["operation"]
    return bulk_editor.operations.render(session, name_str)


def apply_operation(name, modifications, error):
    resp = Response()

    if error is None:
        bulk_editor.apply(session, name, modifications)

    resp.headers['HX-Trigger'] = "notification"
    if error is not None:
        notifications.set_error(session, error)
    else:
        notifications.set_info(session, "Bulk operation complete.")
        resp.headers['HX-Trigger'] += ",update-port"

    return resp


@app.route("/bulk-editor/apply/<name_str>", methods=['POST'])
@errors.handler
def bulk_editor_apply(name_str):
    assert htmx is not None

    error = None
    name = None
    modifications = None
    try:
        name = bulk_editor.operations.from_input(name_str)
        modifications = bulk_editor.get_modifications(session, name)
    except (errors.NotSupportedError, errors.DoesNotExistError) as e:
        error = e

    resp = apply_operation(name, modifications, error)
    html = bulk_editor.render(session)
    resp.response = html
    return resp


@app.route("/bulk-editor", methods=['PUT', 'POST'])
@errors.handler
def bulk_editor_endpoint():
    assert htmx is not None

    match request.method:
        case 'PUT':
            resp = Response()
        case 'POST':
            error = None
            name = None
            modifications = None
            try:
                name, modifications = bulk_editor.validate_and_parse(
                    session,
                    request.form,
                )
            except (errors.UserError) as e:
                error = e

            resp = apply_operation(name, modifications, error)

    html = bulk_editor.render(session)
    resp.response = html
    return resp


# TODO: Later, consider supporting an array of notifications
# with timeouts we maintain server-side.
@app.route("/notification/<show>", methods=['PUT'])
@errors.handler
def notification(show):
    assert htmx is not None

    show_notifications = show == "on"
    if not show_notifications:
        notifications.reset(session)

    return notifications.render(session, show_notifications)


@app.route("/navigator/toggle", methods=['PUT'])
@errors.handler
def navigator_toggler():
    assert htmx is not None

    show_navigator = command_palette.get_show_navigator(session)
    command_palette.set_show_navigator(session, not show_navigator)

    html = navigator.render(session)
    return html


@app.route("/navigator/target", methods=['PUT', 'POST'])
@errors.handler
def navigator_target():
    assert htmx is not None

    resp = Response()
    resp.headers['HX-Trigger'] = "update-port"
    match request.method:
        case 'POST':
            error = None
            try:
                navigator.set_target(session)
            except errors.NotSupportedError as e:
                error = e

            if error is not None:
                notifications.set_error(session, error)
            else:
                notifications.set_info(
                    session,
                    "Targeting cell position in port.",
                )
            resp.headers['HX-Trigger'] += ",notification"

    navigator_target_html = navigator.render_target(session)
    resp.response = navigator_target_html
    return resp


@app.route("/navigator/move/<method>", methods=['PUT'])
@errors.handler
def navigator_move(method):
    assert htmx is not None

    navigator.move_upperleft(session, method)

    notifications.set_info(session, "Moved port.")
    navigator_html = navigator.render(session)
    resp = Response(navigator_html)
    resp.headers['HX-Trigger'] = "update-port,notification"
    return resp


@app.route("/files/toggle", methods=['PUT'])
@errors.handler
def files_toggler():
    assert htmx is not None

    show_files = command_palette.get_show_files(session)
    command_palette.set_show_files(session, not show_files)

    html = files.render(session)
    return html


@app.route("/files/import", methods=['POST'])
@errors.handler
def files_import():
    assert htmx is not None

    error = None
    try:
        files.import_from(request)
    except errors.UserError as e:
        error = e

    if error is None:
        notifications.set_info(session, "Imported file.")
    else:
        notifications.set_error(session, error)

    port_html = port.render(session)
    resp = Response(port_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/files/export", methods=['POST'])
@errors.handler
def files_export():
    assert htmx is not None

    error = None
    try:
        files.export_to(request)
    except errors.UserError as e:
        error = e

    if error is None:
        notifications.set_info(session, "Exported file.")
    else:
        notifications.set_error(session, error)

    null_html = render_null(session)
    resp = Response(null_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/files/open", methods=['POST'])
@errors.handler
def files_open():
    assert htmx is not None

    error = None
    try:
        files.open_from(request)
    except errors.UserError as e:
        error = e

    if error is None:
        notifications.set_info(session, "Open file.")
    else:
        notifications.set_error(session, error)

    port_html = port.render(session)
    resp = Response(port_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/files/save", methods=['POST'])
@errors.handler
def files_save():
    assert htmx is not None

    error = None
    try:
        files.save_to(request)
    except errors.UserError as e:
        error = e

    if error is None:
        notifications.set_info(session, "Saved file.")
    else:
        notifications.set_error(session, error)

    null_html = render_null(session)
    resp = Response(null_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/settings/toggle", methods=['PUT'])
@errors.handler
def settings_toggler():
    assert htmx is not None

    show_settings = command_palette.get_show_settings(session)
    command_palette.set_show_settings(session, not show_settings)

    html = settings.render(session)
    return html


@app.route("/settings/render-mode/<render_mode>", methods=['PUT'])
@errors.handler
def render_mode(render_mode):
    assert htmx is not None

    settings.set(session, render_mode)

    notifications.set_info(session, "Updated render mode.")
    resp = Response()
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/navigator/dimensions", methods=['PUT'])
@errors.handler
def navigator_dimensions():
    assert htmx is not None

    nrows = int(request.form['nrows'])
    ncols = int(request.form['ncols'])
    navigator.set_dimensions(session, nrows, ncols)

    notifications.set_info(session, "Updated view dimensions.")
    port_html = port.render(session)
    resp = Response(port_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/navigator/move-increments", methods=['PUT'])
@errors.handler
def navigator_move_increments():
    assert htmx is not None

    mrows = int(request.form['mrows'])
    mcols = int(request.form['mcols'])
    navigator.set_move_increments(session, mrows, mcols)

    notifications.set_info(session, "Updated move increments.")
    port_html = port.render(session)
    resp = Response(port_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
