from flask import (
    Flask,
    render_template,
    session,
    request,
    Response,
)
from flask_htmx import HTMX
from waitress import serve

import src.errors as errors
import src.port as port
import src.bulk_edit as bulk_edit
import src.modes as modes
import src.notifications as notifications
import src.settings as settings

import src.data.sheet as sheet
import src.data.selections as selections
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
    bulk_edit_html = bulk_edit.render(session)
    settings_html = settings.render(session)
    body = render_template(
            "partials/body.html",
            show_help=help_state,
            notification_banner=notification_banner,
            data=port_html,
            editor=editor,
            bulk_edit=bulk_edit_html,
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


@app.route("/help", methods=['PUT'])
@errors.handler
def toggle_help():
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

    cell_position = selections.CellPosition(
        row_index=selections.RowIndex(int(row)),
        col_index=selections.ColIndex(int(col)),
    )
    highlight = state == "on"

    return port.render_cell(session, cell_position, highlight=highlight)


@app.route("/cell/<row>/<col>/update", methods=['PUT'])
@errors.handler
def cell_rerender(row, col):
    assert htmx is not None

    # May come from:
    # 1. A submission by the editor.

    cell_position = selections.CellPosition(
        row_index=selections.RowIndex(int(row)),
        col_index=selections.ColIndex(int(col)),
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
    cell_position = selections.CellPosition(
        row_index=selections.RowIndex(int(row)),
        col_index=selections.ColIndex(int(col)),
    )
    key = f"input-cell-{row}-{col}"
    if key in request.form:
        value = request.form[key]
        operations.update_cell(cell_position, value)

    # Sync with editor.
    port.set_focused_cell_position(session, cell_position)
    return render_editor(session)


@app.route("/editor", methods=['GET', 'PUT'])
@errors.handler
def editor():
    assert htmx is not None

    resp = Response()
    match request.method:
        case 'PUT':
            # toggle mode
            editor_state = modes.check(session, "Editor")
            modes.set(session, "Editor", not editor_state)
            resp.headers['HX-Trigger'] = "modes"

    html = render_editor(session)
    resp.response = html
    return resp


@app.route("/bulk-edit", methods=['PUT', 'POST'])
@errors.handler
def open_bulk_edit():
    assert htmx is not None

    resp = Response()
    resp.headers['HX-Trigger'] = "modes"

    match request.method:
        case 'PUT':
            # toggle mode
            bulk_edit_state = modes.check(session, "Bulk-Edit")
            modes.set(session, "Bulk-Edit", not bulk_edit_state)
        case 'POST':
            success = False
            try:
                bulk_edit.attempt_apply(session, request.form)
                success = True
            except (errors.UserError, errors.OutOfBoundsError) as e:
                notifications.set(session, notifications.Notification(
                    message=str(e),
                    mode=notifications.Mode.ERROR,
                ))
                resp.headers['HX-Trigger'] += ",notification"

            if success:
                notifications.set(session, notifications.Notification(
                    message="Bulk operation complete.",
                    mode=notifications.Mode.INFO,
                ))
                resp.headers['HX-Trigger'] += ",notification"
                resp.headers['HX-Trigger'] += ",update-port"

    html = bulk_edit.render(session)
    resp.response = html
    return resp


@app.route("/bulk-edit/operation-form", methods=['GET'])
@errors.handler
def bulk_edit_operation_form():
    assert htmx is not None

    operation = request.args["operation"]
    return bulk_edit.operations.render(session, operation)


@app.route("/bulk-edit/selection-inputs", methods=['GET'])
@errors.handler
def bulk_edit_selection_inputs():
    assert htmx is not None

    mode = request.args["selection-mode"]
    return bulk_edit.selection.render_inputs(session, mode)


@app.route("/navigator", methods=['PUT', 'POST'])
@errors.handler
def navigator():
    assert htmx is not None

    resp = Response()
    resp.headers['HX-Trigger'] = "modes"

    match request.method:
        case 'PUT':
            # toggle mode
            navigator_state = modes.check(session, "Navigator")
            modes.set(session, "Navigator", not navigator_state)

    html = render_navigator(session)
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


@app.route("/settings", methods=['PUT'])
@errors.handler
def toggle_settings():
    assert htmx is not None

    resp = Response()
    resp.headers['HX-Trigger'] = "modes"

    match request.method:
        case 'PUT':
            # toggle mode
            settings_state = modes.check(session, "Settings")
            modes.set(session, "Settings", not settings_state)

    html = settings.render(session)
    resp.response = html
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
