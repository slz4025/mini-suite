from flask import (
    render_template,
    Response,
)
import json
import os

from settings import Settings

import src.errors.types as err_types
import src.errors as errors
import src.sheet as sheet
import src.command_palette as command_palette
import src.notifications as notifications
import src.port as port
import src.editor as editor
import src.selector as selector
import src.bulk_editor as bulk_editor
import src.viewer as viewer


class Session:
    def __init__(self, path, debug):
        self.path = path
        sheet.files.setup(path, debug)

        notifications.state.init()

    def add_event(self, resp, event):
        if 'HX-Trigger' not in resp.headers:
            resp.headers['HX-Trigger'] = ""
        events = resp.headers['HX-Trigger'].split(",")
        if event not in events:
            resp.headers['HX-Trigger'] += "," + event

    def notify_info(self, resp, message):
        self.add_event(resp, "notification")
        notifications.state.set_info(message)

    def notify_error(self, resp, error):
        self.add_event(resp, "notification")
        notifications.state.set_error(error)

    def reset_notifications(self, resp):
        self.add_event(resp, "notification")
        notifications.state.reset()

    def render_null_helper(self, session):
        return render_template("partials/null.html")

    def render_port_helper(self, resp, session, show_errors=True):
        port_html = port.render(session, catch_failure=True)

        try:
            if show_errors:
                port_html = port.render(session)
        except err_types.UserError as e:
            self.notify_error(resp, e)

        return port_html

    def render_cell_helper(self, resp, session, cell_position):
        cell_html = port.render_cell(
            session,
            cell_position,
            catch_failure=True,
        )

        try:
            cell_html = port.render_cell(session, cell_position)
        except err_types.UserError as e:
            self.notify_error(resp, e)

        self.add_event(resp, "editor")
      
        return cell_html

    def render_body_helper(self, resp, session):
        dark_mode = Settings.DARK_MODE
        show_command_palette = command_palette.state.get_show()

        null = self.render_null_helper(session)
        command_palette_html = command_palette.render(session)
        port_html = self.render_port_helper(resp, session)
        # render last in case set any notifications from previous steps
        notification_html = notifications.render(False)

        body = render_template(
                "partials/body.html",
                dark_mode=dark_mode,
                null=null,
                notification_banner=notification_html,
                command_palette=command_palette_html,
                data=port_html,
                show_command_palette=show_command_palette,
                )

        _, basename = os.path.split(self.path)
        body_html = render_template(
            "index.html",
            body=body,
            tab_name=basename,
            )
        return body_html

    def render_error(self, logger):
        resp = Response()

        error_message = errors.state.get_message()
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

    def root(self, session):
        resp = Response()

        command_palette.state.init()
        viewer.state.init()

        body_html = self.render_body_helper(resp, session)
        resp.set_data(body_html)
        return resp

    def toggle_command_palette(self, session):
        resp = Response()

        show_command_palette = command_palette.state.get_show()
        command_palette.state.set_show(not show_command_palette)

        body_html = self.render_body_helper(resp, session)
        resp.set_data(body_html)
        return resp

    def save(self, session):
        resp = Response()

        sheet.files.save()

        self.notify_info(resp, "Saved file.")

        null_html = self.render_null_helper(session)
        resp.set_data(null_html)
        return resp

    def toggle_help(self, session):
        resp = Response()

        show_help = command_palette.state.get_show_help()
        command_palette.state.set_show_help(not show_help)

        command_palette_html = command_palette.render(session)
        resp.set_data(command_palette_html)
        return resp

    def render_port(self, session):
        resp = Response()

        port_html = self.render_port_helper(resp, session)
        resp.set_data(port_html)
        return resp

    def render_cell(self, session, cell_position):
        resp = Response()

        cell_html = self.render_cell_helper(resp, session, cell_position)
        resp.set_data(cell_html)
        return resp

    def focus_cell(self, session, cell_position):
        resp = Response()

        prev_focused_cell_position = editor.state.get_focused_cell_position()

        editor.state.set_focused_cell_position(cell_position)

        # Re-render former focused cell to show computed value.
        if prev_focused_cell_position is not None and prev_focused_cell_position != cell_position:
            row = prev_focused_cell_position.row_index.value
            col = prev_focused_cell_position.col_index.value
            self.add_event(resp, f"cell-{row}-{col}")

        self.add_event(resp, 'editor')

        cell_html = self.render_cell_helper(resp, session, cell_position)
        resp.set_data(cell_html)
        return resp

    def update_cell_helper(self, resp, session, cell_position, value):
        try:
            sheet.update_cell_value(cell_position, value)
            dep_cells = sheet.get_potential_dependents()
            for dc in dep_cells:
                if dc == cell_position:
                    continue
                row = dc.row_index.value
                col = dc.col_index.value
                self.add_event(resp, f"cell-{row}-{col}")
            return True
        except (err_types.UserError) as e:
            self.notify_error(resp, e)
            return False

    def update_cell(self, session, cell_position, value):
        resp = Response()

        success = self.update_cell_helper(resp, session, cell_position, value)
        if success:
            self.notify_info(resp, "Updated cell value successfully.")

        cell_html = self.render_cell_helper(resp, session, cell_position)
        resp.set_data(cell_html)
        return resp

    def sync_cell(self, session, cell_position, value):
        resp = Response()

        success = self.update_cell_helper(resp, session, cell_position, value)
        if success:
            # Clear errors, most likely caused by updating cell.
            # Note that this may clear unrelated errors too.
            self.reset_notifications(resp)

        editor_html = editor.render(session)
        resp.set_data(editor_html)
        return resp

    def toggle_editor(self, session):
        resp = Response()

        show_editor = command_palette.state.get_show_editor()
        command_palette.state.set_show_editor(not show_editor)

        editor_html = editor.render(session)
        resp.set_data(editor_html)
        return resp

    def render_editor_operations(self, session):
        resp = Response()

        editor_operations_html = editor.operations.render(session)
        resp.set_data(editor_operations_html)
        return resp

    def preview_editor_operation(self, session, op_name_str):
        resp = Response()

        editor_html = editor.render(session, op_name_str=op_name_str)
        resp.set_data(editor_html)
        return resp

    def render_editor(self, session):
        resp = Response()

        editor_html = editor.render(session)
        resp.set_data(editor_html)
        return resp

    def toggle_selector(self, session):
        resp = Response()

        show_selector = command_palette.state.get_show_selector()
        command_palette.state.set_show_selector(not show_selector)

        selector_html = selector.render(session)
        resp.set_data(selector_html)
        return resp

    def render_selector_input(self, session, mode_str):
        resp = Response()

        mode = selector.modes.from_input(mode_str)

        selector_input_html = selector.inputs.render(session, mode)
        resp.set_data(selector_input_html)
        return resp

    def update_selection_helper(
        self,
        resp,
        session,
        mode,
        sel,
        notify=False,
        reset=False,
        update_port=False,
    ):
        if reset:
            selector.reset(session)
        else:
            selector.save(session, mode, sel)

        if notify:
            self.notify_info(resp, "Selection {}.".format(
                "cleared" if reset else "registered"
            ))

        # Show selection in port.
        if update_port:
            self.add_event(resp, "update-port")

        # Rerender what editor operations are allowed based on selection.
        self.add_event(resp, "editor-operations")
        # Rerender what bulk-editor operations are allowed based on selection.
        self.add_event(resp, "bulk-editor")
        # Update showing viewer target feature.
        self.add_event(resp, "viewer-target")

    def update_selection_from_endpoints(self, session, start, end):
        resp = Response()

        try:
            mode, sel = selector.compute_from_endpoints(start, end)

            self.update_selection_helper(resp, session, mode, sel)
        except (err_types.NotSupportedError) as e:
            self.notify_error(resp, e)

        selector_html = selector.render(session)
        resp.set_data(selector_html)
        return resp

    def move_selection(self, session, direction):
        resp = Response()

        try:
            mode, sel = selector.compute_updated_selector(session, direction)

            self.update_selection_helper(resp, session, mode, sel, update_port=True)
        except (err_types.NotSupportedError) as e:
            self.notify_error(resp, e)

        selector_html = selector.render(session)
        resp.set_data(selector_html)
        return resp

    def update_selection(self, session, form):
        resp = Response()

        try:
            mode, sel = selector.validate_and_parse(session, form)

            self.update_selection_helper(
                resp,
                session,
                mode,
                sel,
                notify=True,
                update_port=True,
            )
        except (err_types.UserError, err_types.OutOfBoundsError) as e:
            self.notify_error(resp, e)

        selector_html = selector.render(session)
        resp.set_data(selector_html)
        return resp

    def delete_selection(self, session):
        resp = Response()

        self.update_selection_helper(
            resp,
            session,
            None,
            None,
            notify=True,
            reset=True,
            update_port=True,
        )

        selector_html = selector.render(session)
        resp.set_data(selector_html)
        return resp

    def toggle_bulk_editor(self, session):
        resp = Response()

        show_bulk_editor = command_palette.state.get_show_bulk_editor()
        command_palette.state.set_show_bulk_editor(not show_bulk_editor)

        bulk_editor_html = bulk_editor.render(session)
        resp.set_data(bulk_editor_html)
        return resp

    def render_bulk_editor_operation(self, session, name_str):
        resp = Response()

        bulk_editor_operations_html = bulk_editor.operations.render(session, name_str)
        resp.set_data(bulk_editor_operations_html)
        return resp

    def apply_bulk_editor_operation(self, session, name_str):
        resp = Response()

        try:
            name = bulk_editor.operations.from_input(name_str)
            modifications = bulk_editor.get_modifications(session, name)

            bulk_editor.apply(session, name, modifications)
            self.add_event(resp, "update-port")
            self.notify_info(resp, "Bulk operation complete.")
        except (err_types.NotSupportedError, err_types.DoesNotExistError) as e:
            self.notify_error(resp, e)

        bulk_editor_html = bulk_editor.render(session)
        resp.set_data(bulk_editor_html)
        return resp

    def render_bulk_editor(self, session):
        resp = Response()

        bulk_editor_html = bulk_editor.render(session)
        resp.set_data(bulk_editor_html)
        return resp

    def apply_bulk_edit(self, session, form):
        resp = Response()

        try:
            name, modifications = bulk_editor.validate_and_parse(
                session,
                form,
            )

            bulk_editor.apply(session, name, modifications)
            self.add_event(resp, "update-port")
            self.notify_info(resp, "Bulk operation complete.")
        except (err_types.UserError) as e:
            self.notify_error(resp, e)

        bulk_editor_html = bulk_editor.render(session)
        resp.set_data(bulk_editor_html)
        return resp

    # TODO: Later, consider supporting an array of notifications
    # with timeouts we maintain server-side.
    def render_notification(self, session, show):
        resp = Response()

        show_notifications = show == "on"
        if not show_notifications:
            self.reset_notifications(resp)

        notification_html = notifications.render(show_notifications)
        resp.set_data(notification_html)
        return resp

    def toggle_viewer(self, session):
        resp = Response()

        show_viewer = command_palette.state.get_show_viewer()
        command_palette.state.set_show_viewer(not show_viewer)

        viewer_html = viewer.render(session)
        resp.set_data(viewer_html)
        return resp

    def render_cell_targeter(self, session):
        resp = Response()

        cell_targeter_html = viewer.render_target(session)
        resp.set_data(cell_targeter_html)
        return resp

    def apply_cell_target(self, session):
        resp = Response()

        try:
            viewer.set_target(session)

            self.add_event(resp, "update-port")
            self.notify_info(resp, "Targeted cell position.")
        except err_types.NotSupportedError as e:
            self.notify_error(resp, e)

        cell_targeter_html = viewer.render_target(session)
        resp.set_data(cell_targeter_html)
        return resp

    def move_port(self, session, method):
        resp = Response()

        viewer.move_upperleft(method)

        self.add_event(resp, "update-port")
        self.notify_info(resp, "Moved port.")

        viewer_html = viewer.render(session)
        resp.set_data(viewer_html)
        return resp

    def update_dimensions(self, session, nrows, ncols):
        resp = Response()

        viewer.state.set_dimensions(nrows, ncols)
        self.notify_info(resp, "Updated view dimensions.")

        port_html = self.render_port_helper(resp, session)
        resp.set_data(port_html)
        return resp
