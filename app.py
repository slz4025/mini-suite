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
import src.errors as errors
import src.modes as modes
import src.notifications as notifications
import src.port as port
import src.selection as selection
import src.settings as settings

import src.data.sheet as sheet
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


def render_editor(session):
    editor_state = modes.check(session, "Editor")
    focused_cell = port.get_focused_cell_position(session)
    row = focused_cell.row_index.value
    col = focused_cell.col_index.value

    data = operations.get_cell(focused_cell)
    if data is None:
        data = ""
    return render_template(
        "partials/editor.html",
        show_editor=editor_state,
        row=row,
        col=col,
        data=data,
    )


def render_navigator(session):
    help_state = modes.check(session, "Help")
    navigator_state = modes.check(session, "Navigator")
    return render_template(
            "partials/navigator.html",
            show_help=help_state,
            show_navigator=navigator_state,
    )


def render_body(session):
    help_state = modes.check(session, "Help")
    notification_banner = notifications.render(session, False)
    port_html = port.render(session)
    navigator = render_navigator(session)
    editor = render_editor(session)
    selection_html = selection.render(session)
    bulk_editor_html = bulk_editor.render(session)
    settings_html = settings.render(session)
    body = render_template(
            "partials/body.html",
            show_help=help_state,
            notification_banner=notification_banner,
            data=port_html,
            editor=editor,
            selection=selection_html,
            bulk_editor=bulk_editor_html,
            navigator=navigator,
            settings=settings_html,
            )
    return body


@app.route("/")
@errors.handler
def root():
    assert htmx is not None

    # TODO: This should eventually be done for the user for the sheet.
    modes.init(session)
    notifications.init(session)
    port.init(session)

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


@app.route("/help/toggle", methods=['PUT'])
@errors.handler
def help_toggler():
    assert htmx is not None

    help_state = modes.check(session, "Help")
    modes.set(session, "Help", not help_state)

    return render_body(session)


@app.route("/modes", methods=['GET'])
@errors.handler
def get_modes_string():
    assert htmx is not None

    modes_string = modes.get_str(session)
    return f"{modes_string}"


@app.route("/port", methods=['PUT'])
@errors.handler
def update_port():
    assert htmx is not None

    return port.render(session)


@app.route("/cell/<row>/<col>/highlight/<state>", methods=['PUT'])
@errors.handler
def cell_highlight(row, col, state):
    assert htmx is not None

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )
    highlight = state == "on"

    return port.render_cell(session, cell_position, editing=highlight)


@app.route("/cell/<row>/<col>/update", methods=['PUT'])
@errors.handler
def cell_rerender(row, col):
    assert htmx is not None

    # May come from:
    # 1. A submission by the editor.

    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )

    key = f"input-cell-{row}-{col}"
    value = request.form[key]
    operations.update_cell(cell_position, value)

    cell = port.render_cell(session, cell_position)
    resp = Response(cell)
    return resp


@app.route("/cell/<row>/<col>/edit", methods=['PUT'])
@errors.handler
def cell_sync(row, col):
    assert htmx is not None

    # May come from:
    # 1. A focusin on the cell,
    # 2. An update on the cell value.

    # Update cell.
    cell_position = selection.types.CellPosition(
        row_index=selection.types.RowIndex(int(row)),
        col_index=selection.types.ColIndex(int(col)),
    )
    key = f"input-cell-{row}-{col}"
    if key in request.form:
        value = request.form[key]
        operations.update_cell(cell_position, value)

    # Sync with editor.
    port.set_focused_cell_position(session, cell_position)
    return render_editor(session)


@app.route("/editor/toggle", methods=['PUT'])
@errors.handler
def editor_toggler():
    assert htmx is not None

    editor_state = modes.check(session, "Editor")
    modes.set(session, "Editor", not editor_state)

    html = render_editor(session)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "modes"
    return resp


@app.route("/editor", methods=['PUT'])
@errors.handler
def editor():
    assert htmx is not None

    html = render_editor(session)
    resp = Response(html)
    return resp


@app.route("/selection/toggle", methods=['PUT'])
@errors.handler
def selection_toggler():
    assert htmx is not None

    selection_state = modes.check(session, "Selection")
    modes.set(session, "Selection", not selection_state)

    html = selection.render(session)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "modes"
    return resp


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
        notifications.set(session, notifications.Notification(
            message=str(error),
            mode=notifications.Mode.ERROR,
        ))
    else:
        if reset:
            selection.reset(session)
        else:
            selection.save(session, mode, sel)

        notifications.set(session, notifications.Notification(
            message="Selection {}.".format(
                "cleared" if reset else "registered"
            ),
            mode=notifications.Mode.INFO,
        ))

        # Rerender what operations are allowed based on selection.
        resp.headers['HX-Trigger'] += ",bulk-editor"
        # Show selection in port.
        resp.headers['HX-Trigger'] += ",update-port"

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

    bulk_editor_state = modes.check(session, "Bulk-Editor")
    modes.set(session, "Bulk-Editor", not bulk_editor_state)

    html = bulk_editor.render(session)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "modes"
    return resp


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
        notifications.set(session, notifications.Notification(
            message=str(error),
            mode=notifications.Mode.ERROR,
        ))
    else:
        notifications.set(session, notifications.Notification(
            message="Bulk operation complete.",
            mode=notifications.Mode.INFO,
        ))

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


@app.route("/navigator/toggle", methods=['PUT'])
@errors.handler
def navigator_toggler():
    assert htmx is not None

    navigator_state = modes.check(session, "Navigator")
    modes.set(session, "Navigator", not navigator_state)

    html = render_navigator(session)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "modes"
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


@app.route("/move/center", methods=['PUT'])
@errors.handler
def center():
    assert htmx is not None

    success = False
    try:
        port.set_center(session, request.form)
        success = True
    except (errors.UserError, errors.OutOfBoundsError) as e:
        notifications.set(session, notifications.Notification(
            message=str(e),
            mode=notifications.Mode.ERROR,
        ))

    if success:
        notifications.set(session, notifications.Notification(
            message="Updated centered cell.",
            mode=notifications.Mode.INFO,
        ))

    port_html = port.render(session)
    resp = Response(port_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/move/<method>", methods=['PUT'])
@errors.handler
def move(method):
    assert htmx is not None

    port.move_upperleft(session, method)

    return port.render(session)


@app.route("/settings/toggle", methods=['PUT'])
@errors.handler
def settings_toggler():
    assert htmx is not None

    settings_state = modes.check(session, "Settings")
    modes.set(session, "Settings", not settings_state)

    html = settings.render(session)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "modes"
    return resp


@app.route("/settings/render-mode/<render_mode>", methods=['PUT'])
@errors.handler
def render_mode(render_mode):
    assert htmx is not None

    settings.set(session, render_mode)
    notifications.set(session, notifications.Notification(
        message="Updated render mode.",
        mode=notifications.Mode.INFO,
    ))

    resp = Response()
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/settings/mrows", methods=['PUT'])
@errors.handler
def mrows():
    assert htmx is not None

    mrows = int(request.form['mrows'])
    settings.set(session, mrows=mrows)
    notifications.set(session, notifications.Notification(
        message="Updated row increments.",
        mode=notifications.Mode.INFO,
    ))

    port_html = port.render(session)
    resp = Response(port_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/settings/mcols", methods=['PUT'])
@errors.handler
def mcols():
    assert htmx is not None

    mcols = int(request.form['mcols'])
    settings.set(session, mcols=mcols)
    notifications.set(session, notifications.Notification(
        message="Updated column increments.",
        mode=notifications.Mode.INFO,
    ))

    port_html = port.render(session)
    resp = Response(port_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/settings/nrows", methods=['PUT'])
@errors.handler
def nrows():
    assert htmx is not None

    nrows = int(request.form['nrows'])
    settings.set(session, nrows=nrows)
    notifications.set(session, notifications.Notification(
        message="Updated # of displayed rows.",
        mode=notifications.Mode.INFO,
    ))

    port_html = port.render(session)
    resp = Response(port_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/settings/ncols", methods=['PUT'])
@errors.handler
def ncols():
    assert htmx is not None

    ncols = int(request.form['ncols'])
    settings.set(session, ncols=ncols)
    notifications.set(session, notifications.Notification(
        message="Updated # of displayed columns.",
        mode=notifications.Mode.INFO,
    ))

    port_html = port.render(session)
    resp = Response(port_html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
