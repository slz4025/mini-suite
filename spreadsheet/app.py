from flask import (
    Flask,
    render_template,
    session,
    request,
    Response,
)
from flask_htmx import HTMX
import json
import os
from waitress import serve

from settings import Settings

import src.bulk_editor as bulk_editor
import src.command_palette as command_palette
import src.editor as editor
import src.errors as errors
import src.files as files
import src.port.viewer as viewer
import src.notifications as notifications
import src.port as port
import src.selection as selection

import src.sheet as sheet
import src.computer as computer


app = Flask(__name__)
htmx = HTMX(app)
app.config.from_object('config.Config')


tab_name = None


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


def add_event(resp, event):
    if 'HX-Trigger' not in resp.headers:
        resp.headers['HX-Trigger'] = ""
    events = resp.headers['HX-Trigger'].split(",")
    if event not in events:
        resp.headers['HX-Trigger'] += "," + event


def notify_info(resp, session, message):
    add_event(resp, "notification")
    notifications.set_info(session, message)


def notify_error(resp, session, error):
    add_event(resp, "notification")
    notifications.set_error(session, error)


def render_port(resp, session, show_errors=True):
    port_html = port.render(session, catch_failure=True)

    try:
        if show_errors:
            port_html = port.render(session)
    except errors.UserError as e:
        notify_error(resp, session, e)

    return port_html


def render_cell(resp, session, cell_position):
    cell_html = port.render_cell(
        session,
        cell_position,
        catch_failure=True,
    )

    try:
        cell_html = port.render_cell(session, cell_position)
    except errors.UserError as e:
        notify_error(resp, session, e)

    add_event(resp, "editor")
    return cell_html


def render_body(resp, session):
    dark_mode = Settings.DARK_MODE
    null = render_null(session)
    show_command_palette = command_palette.state.get_show(session)
    command_palette_html = command_palette.render(session)
    port_html = render_port(resp, session)
    # render last in case set any notifications from previous steps
    notification_banner = notifications.render(session, False)
    body = render_template(
            "partials/body.html",
            dark_mode=dark_mode,
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

    command_palette.init(session)
    notifications.init(session)
    viewer.init(session)

    resp = Response()
    body = render_body(resp, session)
    html = render_template(
        "index.html",
        body=body,
        tab_name=tab_name,
        )
    resp.set_data(html)
    return resp


@app.route("/command-palette/toggle", methods=['PUT'])
@errors.handler
def command_palette_toggle():
    assert htmx is not None

    show_command_palette = command_palette.state.get_show(session)
    command_palette.state.set_show(session, not show_command_palette)

    resp = Response()
    body_html = render_body(resp, session)
    resp.set_data(body_html)
    return resp


@app.route("/help/toggle", methods=['PUT'])
@errors.handler
def help_toggler():
    assert htmx is not None

    show_help = command_palette.state.get_show_help(session)
    command_palette.state.set_show_help(session, not show_help)

    return command_palette.render(session)


@app.route("/port", methods=['PUT'])
@errors.handler
def update_port():
    assert htmx is not None

    resp = Response()
    port_html = render_port(resp, session)
    resp.set_data(port_html)
    return resp


@app.route("/cell/<row>/<col>", methods=['PUT'])
@errors.handler
def cell_render(row, col):
    assert htmx is not None

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )

    resp = Response()
    cell_html = render_cell(resp, session, cell_position)
    resp.set_data(cell_html)
    return resp


@app.route("/cell/<row>/<col>/focus", methods=['PUT', 'GET'])
@errors.handler
def cell_focus(row, col):
    assert htmx is not None

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )

    prev_focused_cell_position = editor.state.get_focused_cell_position(session)

    editor.state.set_focused_cell_position(session, cell_position)

    resp = Response()

    # Re-render former focused cell to show computed value.
    if prev_focused_cell_position is not None and prev_focused_cell_position != cell_position:
        row = prev_focused_cell_position.row_index.value
        col = prev_focused_cell_position.col_index.value
        add_event(resp, f"cell-{row}-{col}")

    add_event(resp, 'editor')

    cell_html = render_cell(resp, session, cell_position)
    resp.set_data(cell_html)
    return resp


def update_cell(resp, session, cell_position, value):
    try:
        computer.update_cell_value(cell_position, value)
        dep_cells = computer.get_potential_dependents(session)
        for dc in dep_cells:
            if dc == cell_position:
                continue
            row = dc.row_index.value
            col = dc.col_index.value
            add_event(resp, f"cell-{row}-{col}")
        return True
    except (errors.UserError) as e:
        notify_error(resp, session, e)
        return False


@app.route("/cell/<row>/<col>/update", methods=['PUT'])
@errors.handler
def cell_update(row, col):
    assert htmx is not None

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )

    key = f"input-cell-{row}-{col}"
    value = request.form[key]

    resp = Response()

    success = update_cell(resp, session, cell_position, value)
    if success:
        notify_info(resp, session, "Updated cell value successfully.")

    cell_html = render_cell(resp, session, cell_position)
    resp.set_data(cell_html)
    return resp


@app.route("/cell/<row>/<col>/sync", methods=['PUT'])
@errors.handler
def cell_sync(row, col):
    assert htmx is not None

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )

    row = cell_position.row_index.value
    col = cell_position.col_index.value
    key = f"input-cell-{row}-{col}"
    if key not in request.form:
        return
    value = request.form[key]

    resp = Response()

    success = update_cell(resp, session, cell_position, value)
    if success:
        # Clear errors, most likely caused by updating cell.
        # Note that this may clear unrelated errors too.
        add_event(resp, "notification")
        notifications.reset(session)

    editor_html = editor.render(session)
    resp.set_data(editor_html)
    return resp


@app.route("/editor/toggle", methods=['PUT'])
@errors.handler
def editor_toggler():
    assert htmx is not None

    show_editor = command_palette.state.get_show_editor(session)
    command_palette.state.set_show_editor(session, not show_editor)

    html = editor.render(session)
    return html


@app.route("/editor/operations", methods=['PUT'])
@errors.handler
def editor_operations():
    assert htmx is not None

    return editor.operations.render(session)


@app.route("/editor/operation/<op_name_str>", methods=['PUT'])
@errors.handler
def editor_operation(op_name_str):
    assert htmx is not None

    html = editor.render(session, op_name_str=op_name_str)
    resp = Response(html)
    return resp


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

    show_selection = command_palette.state.get_show_selection(session)
    command_palette.state.set_show_selection(session, not show_selection)

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
    return selection.inputs.render(session, mode)


def update_selection(
    resp,
    mode,
    sel,
    notify=False,
    reset=False,
    update_port=False,
):
    if reset:
        selection.reset(session)
    else:
        selection.save(session, mode, sel)

    if notify:
        notify_info(resp, session, "Selection {}.".format(
            "cleared" if reset else "registered"
        ))

    # Show selection in port.
    if update_port:
        add_event(resp, "update-port")

    # Rerender what editor operations are allowed based on selection.
    add_event(resp, "editor-operations")
    # Rerender what bulk-editor operations are allowed based on selection.
    add_event(resp, "bulk-editor")
    # Update showing port-viewer target feature.
    add_event(resp, "port-viewer-target")


@app.route(
    "/selection/start/<start_row>/<start_col>/end/<end_row>/<end_col>",
    methods=['PUT'],
)
@errors.handler
def selection_start_end(start_row, start_col, end_row, end_col):
    assert htmx is not None

    start = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(start_row)),
        col_index=selection.types.ColIndex(int(start_col)),
    )
    end = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(end_row)),
        col_index=selection.types.ColIndex(int(end_col)),
    )

    resp = Response()

    try:
        mode, sel = selection.compute_from_endpoints(start, end)

        update_selection(resp, mode, sel)
    except (errors.NotSupportedError) as e:
        notify_error(resp, session, e)

    selection_html = selection.render(session)
    resp.set_data(selection_html)
    return resp


@app.route("/selection/move/<direction>", methods=['PUT'])
@errors.handler
def selection_move(direction):
    assert htmx is not None

    resp = Response()

    try:
        mode, sel = selection.compute_updated_selection(session, direction)

        update_selection(resp, mode, sel, update_port=True)
    except (errors.NotSupportedError) as e:
        notify_error(resp, session, e)

    selection_html = selection.render(session)
    resp.set_data(selection_html)
    return resp


@app.route("/selection", methods=['POST', 'DELETE'])
@errors.handler
def selection_endpoint():
    assert htmx is not None

    resp = Response()

    match request.method:
        case 'POST':
            try:
                mode, sel = selection.validate_and_parse(session, request.form)

                update_selection(
                    resp,
                    mode,
                    sel,
                    notify=True,
                    update_port=True,
                )
            except (errors.UserError, errors.OutOfBoundsError) as e:
                notify_error(resp, session, e)
        case 'DELETE':
            update_selection(
                resp,
                None,
                None,
                notify=True,
                reset=True,
                update_port=True,
            )

    selection_html = selection.render(session)
    resp.set_data(selection_html)
    return resp


@app.route("/bulk-editor/toggle", methods=['PUT'])
@errors.handler
def bulk_editor_toggler():
    assert htmx is not None

    show_bulk_editor = command_palette.state.get_show_bulk_editor(session)
    command_palette.state.set_show_bulk_editor(session, not show_bulk_editor)

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


@app.route("/bulk-editor/apply/<name_str>", methods=['POST'])
@errors.handler
def bulk_editor_apply(name_str):
    assert htmx is not None

    resp = Response()

    try:
        name = bulk_editor.operations.from_input(name_str)
        modifications = bulk_editor.get_modifications(session, name)

        bulk_editor.apply(session, name, modifications)
        add_event(resp, "update-port")
        notify_info(resp, session, "Bulk operation complete.")
    except (errors.NotSupportedError, errors.DoesNotExistError) as e:
        notify_error(resp, session, e)

    bulk_editor_html = bulk_editor.render(session)
    resp.set_data(bulk_editor_html)
    return resp


@app.route("/bulk-editor", methods=['PUT', 'POST'])
@errors.handler
def bulk_editor_endpoint():
    assert htmx is not None

    resp = Response()

    match request.method:
        case 'POST':
            try:
                name, modifications = bulk_editor.validate_and_parse(
                    session,
                    request.form,
                )

                bulk_editor.apply(session, name, modifications)
                add_event(resp, "update-port")
                notify_info(resp, session, "Bulk operation complete.")
            except (errors.UserError) as e:
                notify_error(resp, session, e)

    bulk_editor_html = bulk_editor.render(session)
    resp.set_data(bulk_editor_html)
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


@app.route("/port-viewer/toggle", methods=['PUT'])
@errors.handler
def port_viewer_toggler():
    assert htmx is not None

    show_port_viewer = command_palette.state.get_show_port_viewer(session)
    command_palette.state.set_show_port_viewer(session, not show_port_viewer)

    html = viewer.render(session)
    return html


@app.route("/port-viewer/target", methods=['PUT', 'POST'])
@errors.handler
def port_viewer_target():
    assert htmx is not None

    resp = Response()

    match request.method:
        case 'POST':
            try:
                viewer.set_target(session)

                add_event(resp, "update-port")
                notify_info(resp, session, "Targeted cell position.")
            except errors.NotSupportedError as e:
                notify_error(resp, session, e)

    port_viewer_target_html = viewer.render_target(session)
    resp.set_data(port_viewer_target_html)
    return resp


@app.route("/port-viewer/move/<method>", methods=['PUT'])
@errors.handler
def port_viewer_move(method):
    assert htmx is not None

    viewer.move_upperleft(session, method)

    resp = Response()
    add_event(resp, "update-port")
    notify_info(resp, session, "Moved port.")

    port_viewer_html = viewer.render(session)
    resp.set_data(port_viewer_html)
    return resp


@app.route("/files/save", methods=['POST'])
@errors.handler
def files_save():
    assert htmx is not None

    files.save()

    resp = Response()

    notify_info(resp, session, "Saved file.")

    null_html = render_null(session)
    resp.set_data(null_html)
    return resp


@app.route("/port-viewer/dimensions", methods=['PUT'])
@errors.handler
def port_viewer_dimensions():
    assert htmx is not None

    nrows = int(request.form['nrows'])
    ncols = int(request.form['ncols'])
    viewer.set_dimensions(session, nrows, ncols)

    resp = Response()

    notify_info(resp, session, "Updated view dimensions.")

    port_html = render_port(resp, session)
    resp.set_data(port_html)
    return resp


def start(port, path, debug):
    global tab_name
    _, basename = os.path.split(path)
    tab_name = basename

    files.setup(path, debug)
    app.logger.info("Starting server")
    serve(app, host='0.0.0.0', port=port)
