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

import src.sheet as sheet
import src.computer as computer


app = Flask(__name__)
htmx = HTMX(app)
app.config.from_object('config.Config')


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


def render_port(resp, session, compute=True, show_errors=True):
    add_event(resp, "editor")
    port_html = port.render(session, compute=compute, catch_failure=True)

    try:
        if compute and show_errors:
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
    dark_mode = app.config["DARK_MODE"]
    null = render_null(session)
    show_command_palette = command_palette.get_show(session)
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
    navigator.init(session)

    resp = Response()
    body = render_body(resp, session)
    body_html = render_template(
        "index.html",
        body=body,
        )
    resp.set_data(body_html)
    return resp


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

    no_compute = "no-compute" in request.args

    resp = Response()
    port_html = render_port(resp, session, compute=not no_compute)
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

    try:
        computer.update_cell_value(cell_position, value)
        notify_info(resp, session, "Updated cell value successfully.")
    except (errors.UserError) as e:
        notify_error(resp, session, e)

    # Re-render the entire port in case other cells depended on the
    # current cell's value.
    port_html = render_port(resp, session, show_errors=False)
    resp.set_data(port_html)
    return resp


@app.route("/cell/<row>/<col>/focus", methods=['PUT'])
@errors.handler
def cell_focus(row, col):
    assert htmx is not None

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )

    editor.state.set_focused_cell_position(session, cell_position)

    html = editor.render(session)
    return html


# Update cell value from within cell.
def update_cell(resp, request, session, cell_position):
    row = cell_position.row_index.value
    col = cell_position.col_index.value

    key = f"input-cell-{row}-{col}"
    if key not in request.form:
        return

    value = request.form[key]
    prev_value = sheet.get_cell_value(cell_position)

    if computer.is_formula(prev_value):
        error = errors.UserError(
            "About to override underlying formula. "
            "Use the editor to view the formula "
            "and update the value instead."
        )
        notify_error(resp, session, error)
    elif computer.is_formula(value):
        error = errors.UserError(
            "Cannot input a formula in the cell. Use the editor instead."
        )
        notify_error(resp, session, error)
    else:
        computer.update_cell_value(cell_position, value)


@app.route("/cell/<row>/<col>/sync", methods=['PUT'])
@errors.handler
def cell_sync(row, col):
    assert htmx is not None

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )

    resp = Response()

    update_cell(resp, request, session, cell_position)

    editor_html = editor.render(session)
    resp.set_data(editor_html)
    return resp


@app.route("/editor/toggle", methods=['PUT'])
@errors.handler
def editor_toggler():
    assert htmx is not None

    show_editor = command_palette.get_show_editor(session)
    command_palette.set_show_editor(session, not show_editor)

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
        add_event(resp, "no-compute-update-port")

    # Rerender what editor operations are allowed based on selection.
    add_event(resp, "editor-operations")
    # Rerender what bulk-editor operations are allowed based on selection.
    add_event(resp, "bulk-editor")
    # Update showing navigator target feature.
    add_event(resp, "navigator-target")


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

        update_selection(mode, sel, update_port=True)
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

    match request.method:
        case 'POST':
            try:
                navigator.set_target(session)

                add_event(resp, "update-port")
                notify_info(resp, session, "Targeted cell position.")
            except errors.NotSupportedError as e:
                notify_error(resp, session, e)

    navigator_target_html = navigator.render_target(session)
    resp.set_data(navigator_target_html)
    return resp


@app.route("/navigator/move/<method>", methods=['PUT'])
@errors.handler
def navigator_move(method):
    assert htmx is not None

    navigator.move_upperleft(session, method)

    resp = Response()
    add_event(resp, "update-port")
    notify_info(resp, session, "Moved port.")

    navigator_html = navigator.render(session)
    resp.set_data(navigator_html)
    return resp


@app.route("/files/toggle", methods=['PUT'])
@errors.handler
def files_toggler():
    assert htmx is not None

    show_files = command_palette.get_show_files(session)
    command_palette.set_show_files(session, not show_files)

    html = files.render(session)
    return html


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


@app.route("/navigator/dimensions", methods=['PUT'])
@errors.handler
def navigator_dimensions():
    assert htmx is not None

    nrows = int(request.form['nrows'])
    ncols = int(request.form['ncols'])
    navigator.set_dimensions(session, nrows, ncols)

    resp = Response()

    notify_info(resp, session, "Updated view dimensions.")

    port_html = render_port(resp, session)
    resp.set_data(port_html)
    return resp


@app.route("/navigator/move-increments", methods=['PUT'])
@errors.handler
def navigator_move_increments():
    assert htmx is not None

    mrows = int(request.form['mrows'])
    mcols = int(request.form['mcols'])
    navigator.set_move_increments(session, mrows, mcols)

    resp = Response()

    notify_info(resp, session, "Updated move increments.")

    navigator_html = navigator.render(session)
    resp.set_data(navigator_html)
    return resp


def start(port, path, debug):
    files.setup(path, debug)

    print(f"Serving on port {port}.")
    serve(app, host='0.0.0.0', port=port)
