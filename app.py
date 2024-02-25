import json
from flask import Flask, render_template, session, request, Response
from flask_htmx import HTMX
from waitress import serve

from src.port import (
    init_port,
    move_upperleft,
    render_port,
    render_cell,
    set_center,
    get_focused_cell,
    set_focused_cell,
)
import src.bulk_edit as bulk_edit
from src.modes import init_modes, check_mode, set_mode, get_modes_str
from src.notifications import (
    NotificationMode,
    Notification,
    init_notifications,
    reset_notifications,
    render_notifications,
    set_notification,
)
from src.settings import init_settings, set_settings, get_settings
from src.sheet import (
    init_sheet,
    get_sheet,
    apply_modification,
    get_cell,
    update_cell,
)
from src.types import Index

app = Flask(__name__)
htmx = HTMX(app)
app.config.from_object('config.Config')


def render_editor(session):
    editor_state = check_mode(session, "Editor")
    focused_cell = get_focused_cell(session)
    row = focused_cell.row
    col = focused_cell.col

    data = get_cell(focused_cell)
    return render_template(
        "partials/editor.html",
        show_editor=editor_state,
        row=row,
        col=col,
        data=data,
    )


def render_navigator(session):
    help_state = check_mode(session, "Help")
    navigator_state = check_mode(session, "Navigator")
    return render_template(
            "partials/navigator.html",
            show_help=help_state,
            show_navigator=navigator_state,
    )


def render_settings(session):
    settings_state = check_mode(session, "Settings")

    settings = get_settings(session)
    return render_template(
        "partials/settings.html",
        show_settings=settings_state,
        render_mode=settings.render_mode,
        mrows=settings.mrows,
        mcols=settings.mcols,
        nrows=settings.nrows,
        ncols=settings.ncols,
    )


def render_body(session):
    help_state = check_mode(session, "Help")
    notification_banner = render_notifications(session, False)
    port = render_port(session)
    navigator = render_navigator(session)
    editor = render_editor(session)
    bulk_edit_controls = bulk_edit.render_controls(session)
    settings_html = render_settings(session)
    body = render_template(
            "partials/body.html",
            show_help=help_state,
            notification_banner=notification_banner,
            data=port,
            editor=editor,
            bulk_edit_controls=bulk_edit_controls,
            navigator=navigator,
            settings=settings_html,
            )
    return body


@app.route("/")
def root():
    assert htmx is not None

    # TODO: This should eventually be done for the user for the sheet.
    init_modes(session)
    init_notifications(session)
    init_port(session)

    # TODO: This should eventually be done for the user
    # or for the user for the sheet.
    init_settings(session)

    # TODO: This should eventually be done only on the creation of the sheet.
    init_sheet(100, 100)

    body = render_body(session)
    return render_template(
        "index.html",
        data=body,
        )


@app.route("/data", methods=['GET'])
def data():
    assert htmx is not None

    sheet = get_sheet()

    data = []
    for row in range(sheet.shape[0]):
        data.append(sheet[row].tolist())

    return json.dumps(data)


@app.route("/help", methods=['PUT'])
def toggle_help():
    assert htmx is not None

    help_state = check_mode(session, "Help")
    set_mode(session, "Help", not help_state)

    return render_body(session)


@app.route("/modes", methods=['GET'])
def modes():
    assert htmx is not None

    modes_string = get_modes_str(session)
    return f"{modes_string}"


@app.route("/port", methods=['PUT'])
def port():
    assert htmx is not None

    port = render_port(session)
    return port


@app.route("/cell/<row>/<col>/highlight/<state>", methods=['PUT'])
def cell_highlight(row, col, state):
    assert htmx is not None

    cell_index = Index(row=int(row), col=int(col))
    highlight = state == "on"

    return render_cell(session, cell_index, highlight=highlight)


@app.route("/cell/<row>/<col>/update", methods=['PUT'])
def cell_rerender(row, col):
    assert htmx is not None

    # May come from:
    # 1. A submission by the editor.

    cell_index = Index(row=int(row), col=int(col))

    key = f"input-cell-{cell_index.row}-{cell_index.col}"
    value = request.form[key]
    update_cell(cell_index, value)

    cell = render_cell(session, cell_index)
    resp = Response(cell)
    return resp


@app.route("/cell/<row>/<col>/edit", methods=['PUT'])
def cell_sync(row, col):
    assert htmx is not None

    # May come from:
    # 1. A focusin on the cell,
    # 2. An update on the cell value.

    # Update cell.
    cell_index = Index(row=int(row), col=int(col))
    key = f"input-cell-{cell_index.row}-{cell_index.col}"
    if key in request.form:
        value = request.form[key]
        update_cell(cell_index, value)

    # Sync with editor.
    set_focused_cell(session, cell_index)
    return render_editor(session)


@app.route("/editor", methods=['GET', 'PUT'])
def editor():
    assert htmx is not None

    resp = Response()
    match request.method:
        case 'PUT':
            # toggle mode
            editor_state = check_mode(session, "Editor")
            set_mode(session, "Editor", not editor_state)
            resp.headers['HX-Trigger'] = "modes"

    html = render_editor(session)
    resp.response = html
    return resp


@app.route("/bulk-edit", methods=['PUT', 'POST'])
def open_bulk_edit():
    assert htmx is not None

    resp = Response()
    resp.headers['HX-Trigger'] = "modes"

    match request.method:
        case 'PUT':
            # toggle mode
            bulk_edit_state = check_mode(session, "Bulk-Edit")
            set_mode(session, "Bulk-Edit", not bulk_edit_state)
        case 'POST':
            success = False
            try:
                modification = bulk_edit.validate_and_parse(request.form)
                apply_modification(modification)
                success = True
            except Exception as e:
                set_notification(session, Notification(
                    message=str(e),
                    mode=NotificationMode.ERROR,
                ))
                resp.headers['HX-Trigger'] += ",notification"

            if success:
                set_notification(session, Notification(
                    message="Bulk updated spreadsheet.",
                    mode=NotificationMode.INFO,
                ))
                resp.headers['HX-Trigger'] += ",notification"
                resp.headers['HX-Trigger'] += ",update-port"

    html = bulk_edit.render_controls(session)
    resp.response = html
    return resp


@app.route("/bulk-edit/operation-form", methods=['GET'])
def bulk_edit_operation_form():
    assert htmx is not None

    operation = request.args["operation"]
    return bulk_edit.render_operation_form(session, operation)


@app.route("/bulk-edit/selection-inputs", methods=['GET'])
def bulk_edit_selection_inputs():
    assert htmx is not None

    mode = request.args["selection-mode"]
    return bulk_edit.render_selection_inputs(session, mode)


@app.route("/navigator", methods=['PUT', 'POST'])
def navigator():
    assert htmx is not None

    resp = Response()
    resp.headers['HX-Trigger'] = "modes"

    match request.method:
        case 'PUT':
            # toggle mode
            navigator_state = check_mode(session, "Navigator")
            set_mode(session, "Navigator", not navigator_state)

    html = render_navigator(session)
    resp.response = html
    return resp


# TODO: Later, consider supporting an array of notifications
# with timeouts we maintain server-side.
@app.route("/notification/<show>", methods=['PUT'])
def notification(show):
    assert htmx is not None

    show_notifications = show == "on"
    if not show_notifications:
        reset_notifications(session)

    return render_notifications(session, show_notifications)


@app.route("/move/center", methods=['PUT'])
def center():
    assert htmx is not None

    success = False
    try:
        set_center(session, request.form)
        success = True
    except Exception as e:
        set_notification(session, Notification(
            message=str(e),
            mode=NotificationMode.ERROR,
        ))

    if success:
        set_notification(session, Notification(
            message="Updated centered cell.",
            mode=NotificationMode.INFO,
        ))

    port = render_port(session)
    resp = Response(port)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/move/<method>", methods=['PUT'])
def move(method):
    assert htmx is not None

    move_upperleft(session, method)

    return render_port(session)


@app.route("/settings", methods=['PUT'])
def toggle_settings():
    assert htmx is not None

    resp = Response()
    resp.headers['HX-Trigger'] = "modes"

    match request.method:
        case 'PUT':
            # toggle mode
            settings_state = check_mode(session, "Settings")
            set_mode(session, "Settings", not settings_state)

    html = render_settings(session)
    resp.response = html
    return resp


@app.route("/settings/render-mode/<render_mode>", methods=['PUT'])
def render_mode(render_mode):
    assert htmx is not None

    set_settings(session, render_mode)
    set_notification(session, Notification(
        message="Updated render mode.",
        mode=NotificationMode.INFO,
    ))

    resp = Response()
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/settings/mrows", methods=['PUT'])
def mrows():
    assert htmx is not None

    mrows = int(request.form['mrows'])
    set_settings(session, mrows=mrows)
    set_notification(session, Notification(
        message="Updated row increments.",
        mode=NotificationMode.INFO,
    ))

    port = render_port(session)
    resp = Response(port)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/settings/mcols", methods=['PUT'])
def mcols():
    assert htmx is not None

    mcols = int(request.form['mcols'])
    set_settings(session, mcols=mcols)
    set_notification(session, Notification(
        message="Updated column increments.",
        mode=NotificationMode.INFO,
    ))

    port = render_port(session)
    resp = Response(port)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/settings/nrows", methods=['PUT'])
def nrows():
    assert htmx is not None

    nrows = int(request.form['nrows'])
    set_settings(session, nrows=nrows)
    set_notification(session, Notification(
        message="Updated # of displayed rows.",
        mode=NotificationMode.INFO,
    ))

    port = render_port(session)
    resp = Response(port)
    resp.headers['HX-Trigger'] = "notification"
    return resp


@app.route("/settings/ncols", methods=['PUT'])
def ncols():
    assert htmx is not None

    ncols = int(request.form['ncols'])
    set_settings(session, ncols=ncols)
    set_notification(session, Notification(
        message="Updated # of displayed columns.",
        mode=NotificationMode.INFO,
    ))

    port = render_port(session)
    resp = Response(port)
    resp.headers['HX-Trigger'] = "notification"
    return resp


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)