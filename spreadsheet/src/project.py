from flask import (
    render_template,
    Response,
)
import json
import os

from settings import Settings

import src.errors as errors
import src.sheet as sheet
import src.command_palette as command_palette
import src.notifications as notifications
import src.port as port
import src.editor as editor
import src.selection as selection
import src.bulk_editor as bulk_editor
import src.port.viewer as viewer


TAB_NAME = None


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


def render_null_helper(session):
    return render_template("partials/null.html")


def render_port_helper(resp, session, show_errors=True):
    port_html = port.render(session, catch_failure=True)

    try:
        if show_errors:
            port_html = port.render(session)
    except errors.UserError as e:
        notify_error(resp, session, e)

    return port_html


def render_cell_helper(resp, session, cell_position):
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


def render_body_helper(resp, session):
    dark_mode = Settings.DARK_MODE
    show_command_palette = command_palette.state.get_show(session)

    null = render_null_helper(session)
    command_palette_html = command_palette.render(session)
    port_html = render_port_helper(resp, session)
    # render last in case set any notifications from previous steps
    notification_html = notifications.render(session, False)

    body = render_template(
            "partials/body.html",
            dark_mode=dark_mode,
            null=null,
            notification_banner=notification_html,
            command_palette=command_palette_html,
            data=port_html,
            show_command_palette=show_command_palette,
            )

    body_html = render_template(
        "index.html",
        body=body,
        tab_name=TAB_NAME,
        )
    return body_html


def render_error(session, logger):
    resp = Response()

    error_message = errors.get_message(session)
    logger.error(error_message)

    user_error_msg = f"""
    <p>
        Encountered unexpected error. Please reload.
        Feel free to report the error with the following stack-trace:
    </p>
    <p>
        {error_message}
    </p>
    """

    resp.set_data(user_error_msg)
    return resp


def root(session):
    resp = Response()

    command_palette.init(session)
    notifications.init(session)
    viewer.init(session)

    body_html = render_body_helper(resp, session)
    resp.set_data(body_html)
    return resp


def toggle_command_palette(session):
    resp = Response()

    show_command_palette = command_palette.state.get_show(session)
    command_palette.state.set_show(session, not show_command_palette)

    body_html = render_body_helper(resp, session)
    resp.set_data(body_html)
    return resp


def save(session):
    resp = Response()

    sheet.files.save()

    notify_info(resp, session, "Saved file.")

    null_html = render_null_helper(session)
    resp.set_data(null_html)
    return resp


def toggle_help(session):
    resp = Response()

    show_help = command_palette.state.get_show_help(session)
    command_palette.state.set_show_help(session, not show_help)

    command_palette_html = command_palette.render(session)
    resp.set_data(command_palette_html)
    return resp


def render_port(session):
    resp = Response()

    port_html = render_port_helper(resp, session)
    resp.set_data(port_html)
    return resp


def render_cell(session, cell_position):
    resp = Response()

    cell_html = render_cell_helper(resp, session, cell_position)
    resp.set_data(cell_html)
    return resp


def focus_cell(session, cell_position):
    resp = Response()

    prev_focused_cell_position = editor.state.get_focused_cell_position(session)

    editor.state.set_focused_cell_position(session, cell_position)

    # Re-render former focused cell to show computed value.
    if prev_focused_cell_position is not None and prev_focused_cell_position != cell_position:
        row = prev_focused_cell_position.row_index.value
        col = prev_focused_cell_position.col_index.value
        add_event(resp, f"cell-{row}-{col}")

    add_event(resp, 'editor')

    cell_html = render_cell_helper(resp, session, cell_position)
    resp.set_data(cell_html)
    return resp


def update_cell_helper(resp, session, cell_position, value):
    try:
        sheet.update_cell_value(cell_position, value)
        dep_cells = sheet.get_potential_dependents(session)
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


def update_cell(session, cell_position, value):
    resp = Response()

    success = update_cell_helper(resp, session, cell_position, value)
    if success:
        notify_info(resp, session, "Updated cell value successfully.")

    cell_html = render_cell_helper(resp, session, cell_position)
    resp.set_data(cell_html)
    return resp


def sync_cell(session, cell_position, value):
    resp = Response()

    success = update_cell_helper(resp, session, cell_position, value)
    if success:
        # Clear errors, most likely caused by updating cell.
        # Note that this may clear unrelated errors too.
        add_event(resp, "notification")
        notifications.reset(session)

    editor_html = editor.render(session)
    resp.set_data(editor_html)
    return resp


def toggle_editor(session):
    resp = Response()

    show_editor = command_palette.state.get_show_editor(session)
    command_palette.state.set_show_editor(session, not show_editor)

    editor_html = editor.render(session)
    resp.set_data(editor_html)
    return resp


def render_editor_operations(session):
    resp = Response()

    editor_operations_html = editor.operations.render(session)
    resp.set_data(editor_operations_html)
    return resp


def preview_editor_operation(session, op_name_str):
    resp = Response()

    editor_html = editor.render(session, op_name_str=op_name_str)
    resp.set_data(editor_html)
    return resp


def render_editor(session):
    resp = Response()

    editor_html = editor.render(session)
    resp.set_data(editor_html)
    return resp


def toggle_selection(session):
    resp = Response()

    show_selection = command_palette.state.get_show_selection(session)
    command_palette.state.set_show_selection(session, not show_selection)

    selection_html = selection.render(session)
    resp.set_data(selection_html)
    return resp


def render_selection_input(session, mode_str):
    resp = Response()

    mode = selection.modes.from_input(mode_str)

    selection_input_html = selection.inputs.render(session, mode)
    resp.set_data(selection_input_html)
    return resp


def update_selection_helper(
    resp,
    session,
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


def update_selection_from_endpoints(session, start, end):
    resp = Response()

    try:
        mode, sel = selection.compute_from_endpoints(start, end)

        update_selection_helper(resp, session, mode, sel)
    except (errors.NotSupportedError) as e:
        notify_error(resp, session, e)

    selection_html = selection.render(session)
    resp.set_data(selection_html)
    return resp


def move_selection(session, direction):
    resp = Response()

    try:
        mode, sel = selection.compute_updated_selection(session, direction)

        update_selection_helper(resp, session, mode, sel, update_port=True)
    except (errors.NotSupportedError) as e:
        notify_error(resp, session, e)

    selection_html = selection.render(session)
    resp.set_data(selection_html)
    return resp


def update_selection(session, form):
    resp = Response()

    try:
        mode, sel = selection.validate_and_parse(session, form)

        update_selection_helper(
            resp,
            session,
            mode,
            sel,
            notify=True,
            update_port=True,
        )
    except (errors.UserError, errors.OutOfBoundsError) as e:
        notify_error(resp, session, e)

    selection_html = selection.render(session)
    resp.set_data(selection_html)
    return resp


def delete_selection(session):
    resp = Response()

    update_selection_helper(
        resp,
        session,
        None,
        None,
        notify=True,
        reset=True,
        update_port=True,
    )

    selection_html = selection.render(session)
    resp.set_data(selection_html)
    return resp


def toggle_bulk_editor(session):
    resp = Response()

    show_bulk_editor = command_palette.state.get_show_bulk_editor(session)
    command_palette.state.set_show_bulk_editor(session, not show_bulk_editor)

    bulk_editor_html = bulk_editor.render(session)
    resp.set_data(bulk_editor_html)
    return resp


def render_bulk_editor_operation(session, name_str):
    resp = Response()

    bulk_editor_operations_html = bulk_editor.operations.render(session, name_str)
    resp.set_data(bulk_editor_operations_html)
    return resp


def apply_bulk_editor_operation(session, name_str):
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


def render_bulk_editor(session):
    resp = Response()

    bulk_editor_html = bulk_editor.render(session)
    resp.set_data(bulk_editor_html)
    return resp


def apply_bulk_edit(session, form):
    resp = Response()

    try:
        name, modifications = bulk_editor.validate_and_parse(
            session,
            form,
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
def render_notification(session, show):
    resp = Response()

    show_notifications = show == "on"
    if not show_notifications:
        notifications.reset(session)

    notification_html = notifications.render(session, show_notifications)
    resp.set_data(notification_html)
    return resp


def toggle_port_viewer(session):
    resp = Response()

    show_port_viewer = command_palette.state.get_show_port_viewer(session)
    command_palette.state.set_show_port_viewer(session, not show_port_viewer)

    viewer_html = viewer.render(session)
    resp.set_data(viewer_html)
    return resp


def render_cell_targeter(session):
    resp = Response()

    cell_targeter_html = viewer.render_target(session)
    resp.set_data(cell_targeter_html)
    return resp


def apply_cell_target(session):
    resp = Response()

    try:
        viewer.set_target(session)

        add_event(resp, "update-port")
        notify_info(resp, session, "Targeted cell position.")
    except errors.NotSupportedError as e:
        notify_error(resp, session, e)

    cell_targeter_html = viewer.render_target(session)
    resp.set_data(cell_targeter_html)
    return resp


def move_port(session, method):
    resp = Response()

    viewer.move_upperleft(session, method)

    add_event(resp, "update-port")
    notify_info(resp, session, "Moved port.")

    viewer_html = viewer.render(session)
    resp.set_data(viewer_html)
    return resp


def update_dimensions(session, nrows, ncols):
    resp = Response()

    viewer.set_dimensions(session, nrows, ncols)
    notify_info(resp, session, "Updated view dimensions.")

    port_html = render_port_helper(resp, session)
    resp.set_data(port_html)
    return resp


def setup(path, debug):
    global TAB_NAME
    _, basename = os.path.split(path)
    TAB_NAME = basename

    sheet.files.setup(path, debug)
