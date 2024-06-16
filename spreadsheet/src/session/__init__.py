from flask import (
    render_template,
    Response,
)
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
        notifications.state.set_info(message)
        self.add_event(resp, "notification")

    def notify_error(self, resp, error):
        notifications.state.set_error(error)
        self.add_event(resp, "notification")

    def reset_notifications(self, resp):
        notifications.state.reset()
        self.add_event(resp, "notification")

    def render_null_helper(self):
        return render_template("partials/null.html")

    def render_port_helper(self, resp, show_errors=True):
        port_html = port.render(catch_failure=True)

        try:
            if show_errors:
                port_html = port.render()
        except err_types.UserError as e:
            self.notify_error(resp, e)

        return port_html

    def render_cell_helper(self, resp, cell_position):
        cell_html = port.render_cell(
            cell_position,
            catch_failure=True,
        )

        try:
            cell_html = port.render_cell(cell_position)
        except err_types.UserError as e:
            self.notify_error(resp, e)

        self.add_event(resp, "editor")
 
        return cell_html

    def render_body_helper(self, resp):
        dark_mode = Settings.DARK_MODE
        show_command_palette = command_palette.state.get_show()
        show_help = command_palette.state.get_show_help()

        null = self.render_null_helper()
        command_palette_html = command_palette.render()
        port_html = self.render_port_helper(resp)
        # render last in case set any notifications from previous steps
        notification_html = notifications.render()

        body_html = render_template(
                "partials/body.html",
                dark_mode=dark_mode,
                null=null,
                notification_banner=notification_html,
                command_palette=command_palette_html,
                data=port_html,
                show_command_palette=show_command_palette,
                show_help=show_help,
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

    def root(self):
        resp = Response()

        command_palette.state.init()
        viewer.state.init()

        body_html = self.render_body_helper(resp)
        _, basename = os.path.split(self.path)
        index_html = render_template(
            "index.html",
            body=body_html,
            tab_name=basename,
            )
        resp.set_data(index_html)
        return resp

    # TODO: Later, consider supporting an array of notifications
    # with timeouts we maintain server-side.
    def render_notification(self, id):
        resp = Response()

        # If we are on same notification, clear.
        curr_id = notifications.state.get_id()
        if id == curr_id:
            self.reset_notifications(resp)

        notification_html = notifications.render()
        resp.set_data(notification_html)
        return resp

    def toggle_command_palette(self):
        resp = Response()

        show_command_palette = command_palette.state.get_show()
        command_palette.state.set_show(not show_command_palette)

        body_html = self.render_body_helper(resp)
        resp.set_data(body_html)
        return resp

    def save(self):
        resp = Response()

        sheet.files.save()

        self.notify_info(resp, "Saved file.")

        null_html = self.render_null_helper()
        resp.set_data(null_html)
        return resp

    def toggle_help(self):
        resp = Response()

        show_help = command_palette.state.get_show_help()
        command_palette.state.set_show_help(not show_help)

        body_html = self.render_body_helper(resp)
        resp.set_data(body_html)
        return resp

    def render_port(self):
        resp = Response()

        port_html = self.render_port_helper(resp)
        resp.set_data(port_html)
        return resp

    def render_cell(self, cell_position):
        resp = Response()

        cell_html = self.render_cell_helper(resp, cell_position)
        resp.set_data(cell_html)
        return resp

    def focus_cell(self, cell_position):
        resp = Response()

        prev_focused_cell_position = editor.state.get_focused_cell_position()

        editor.state.set_focused_cell_position(cell_position)

        # Re-render former focused cell to show computed value.
        if prev_focused_cell_position is not None and prev_focused_cell_position != cell_position:
            row = prev_focused_cell_position.row_index.value
            col = prev_focused_cell_position.col_index.value
            self.add_event(resp, f"cell-{row}-{col}")

        self.add_event(resp, 'editor')

        cell_html = self.render_cell_helper(resp, cell_position)
        resp.set_data(cell_html)
        return resp

    def update_cell_helper(self, resp, cell_position, value):
        try:
            sheet.update_cell_value(cell_position, value)
            dep_cells = sheet.get_potential_dependents()
            for dc in dep_cells:
                if dc == cell_position:
                    continue
                row = dc.row_index.value
                col = dc.col_index.value
                self.add_event(resp, f"cell-{row}-{col}")

            # Clear errors, most likely caused by updating cell.
            # Note that this may clear unrelated errors too.
            self.reset_notifications(resp)
        except (err_types.UserError) as e:
            self.notify_error(resp, e)

    def update_cell(self, cell_position, value):
        resp = Response()

        self.update_cell_helper(resp, cell_position, value)

        cell_html = self.render_cell_helper(resp, cell_position)
        resp.set_data(cell_html)
        return resp

    def sync_cell(self, cell_position, value):
        resp = Response()

        self.update_cell_helper(resp, cell_position, value)

        editor_html = editor.render()
        resp.set_data(editor_html)
        return resp

    def toggle_selector(self):
        resp = Response()

        show_selector = command_palette.state.get_show_selector()
        command_palette.state.set_show_selector(not show_selector)

        selector_html = selector.render()
        resp.set_data(selector_html)
        return resp

    def use_selector_input(self, mode_str):
        resp = Response()

        mode = selector.modes.from_input(mode_str)

        selector_html = selector.render(mode)
        resp.set_data(selector_html)
        return resp

    def update_selection_helper(
        self,
        resp,
        mode,
        sel,
        notify=False,
        reset=False,
        update_port=False,
    ):
        if reset:
            selector.reset()
        else:
            selector.save(mode, sel)

        # TODO: Only notify if user can't see selection.
        if notify:
            self.notify_info(resp, "Selection {}.".format(
                "cleared" if reset else "registered"
            ))

        # Show selection in port.
        if update_port:
            self.add_event(resp, "update-port")

        # Rerender what editor operations are allowed based on selection.
        self.add_event(resp, "editor-operations")
        # Rerender bulk-editor selection users.
        self.add_event(resp, "use-bulk-edit-selection")
        # Update showing viewer target feature.
        self.add_event(resp, "viewer-target")

    def update_search_results(self, text):
        resp = Response()

        selector.search.set_text(text)

        search_results_html = selector.search.render_results()
        resp.set_data(search_results_html)
        return resp

    def update_selector_cell_position(self, pos):
        resp = Response()

        try:
            self.update_selection_helper(resp, selector.types.Mode.CELL_POSITION, pos)
        except (err_types.NotSupportedError) as e:
            e = Exception(f"Could not update selection: {e}")
            self.notify_error(resp, e)

        selector_html = selector.render()
        resp.set_data(selector_html)
        return resp

    def update_selection_from_endpoints(self, start, end):
        resp = Response()

        try:
            mode, sel = selector.compute_from_endpoints(start, end)

            self.update_selection_helper(resp, mode, sel)
        except (err_types.NotSupportedError) as e:
            e = Exception(f"Could not update selection: {e}")
            self.notify_error(resp, e)

        selector_html = selector.render()
        resp.set_data(selector_html)
        return resp

    def move_selection(self, direction):
        resp = Response()

        try:
            mode, sel = selector.compute_updated_selector(direction)

            self.update_selection_helper(resp, mode, sel, update_port=True)
        except (err_types.NotSupportedError) as e:
            e = Exception(f"Could not update selection: {e}")
            self.notify_error(resp, e)

        selector_html = selector.render()
        resp.set_data(selector_html)
        return resp

    def render_selector(self):
        resp = Response()

        selector_html = selector.render()
        resp.set_data(selector_html)
        return resp

    def update_selection(self, form):
        resp = Response()

        try:
            mode, sel = selector.validate_and_parse(form)

            self.update_selection_helper(
                resp,
                mode,
                sel,
                notify=True,
                update_port=True,
            )
        except (err_types.UserError, err_types.OutOfBoundsError) as e:
            e = Exception(f"Could not update selection: {e}")
            self.notify_error(resp, e)

        selector_html = selector.render()
        resp.set_data(selector_html)
        return resp

    def delete_selection(self):
        resp = Response()

        self.update_selection_helper(
            resp,
            None,
            None,
            notify=True,
            reset=True,
            update_port=True,
        )

        selector_html = selector.render()
        resp.set_data(selector_html)
        return resp

    def toggle_editor(self):
        resp = Response()

        show_editor = command_palette.state.get_show_editor()
        command_palette.state.set_show_editor(not show_editor)

        editor_html = editor.render()
        resp.set_data(editor_html)
        return resp

    def render_editor_operations(self):
        resp = Response()

        editor_operations_html = editor.operations.render()
        resp.set_data(editor_operations_html)
        return resp

    def preview_editor_operation(self, op_name):
        resp = Response()

        editor_html = editor.render(op_name=op_name)
        resp.set_data(editor_html)
        return resp

    def render_editor(self):
        resp = Response()

        editor_html = editor.render()
        resp.set_data(editor_html)
        return resp

    def toggle_bulk_editor(self):
        resp = Response()

        show_bulk_editor = command_palette.state.get_show_bulk_editor()
        command_palette.state.set_show_bulk_editor(not show_bulk_editor)

        bulk_editor_html = bulk_editor.render()
        resp.set_data(bulk_editor_html)
        return resp

    def use_bulk_editor_operation(self, name):
        resp = Response()

        bulk_editor.operations.state.set_current_operation(name)
        bulk_editor.operations.state.reset_selections()

        bulk_editor_operations_html = bulk_editor.operations.render(name)
        resp.set_data(bulk_editor_operations_html)
        return resp

    def render_bulk_editor_use_selection(self, name, use):
        resp = Response()

        use_selection_html = bulk_editor.operations.selection.render(name, use)
        resp.set_data(use_selection_html)
        return resp

    def add_bulk_editor_selection(self, name, use):
        resp = Response()

        selection = selector.state.get_selection()

        curr_name = bulk_editor.operations.state.get_current_operation()
        assert curr_name == name
        operation = bulk_editor.operations.get(curr_name)

        try:
            bulk_editor.operations.selection.add(use, operation, selection)
            self.notify_info(resp, f"Inputted selection for {name}.")
        except (err_types.NotSupportedError, err_types.UserError, err_types.DoesNotExistError) as e:
            e = Exception(f"Could not input selection for {name}: {e}")
            self.notify_error(resp, e)

        use_selection_html = bulk_editor.operations.selection.render(name, use)
        resp.set_data(use_selection_html)
        return resp

    def render_bulk_editor(self):
        resp = Response()

        bulk_editor_html = bulk_editor.render()
        resp.set_data(bulk_editor_html)
        return resp

    def apply_bulk_editor_shortcut(self, shortcut):
        name, form, sels = bulk_editor.get_shortcut_inputs(shortcut)

        bulk_editor.operations.state.set_current_operation(name)
        operation = bulk_editor.operations.get(name)

        bulk_editor.operations.state.reset_selections()
        for k, v in sels.items():
            bulk_editor.operations.selection.add(k, operation, v)

        return self.apply_bulk_edit(form)

    def apply_bulk_edit(self, form):
        resp = Response()

        name = bulk_editor.operations.state.get_current_operation()

        try:
            bulk_editor.apply(name, form)
            self.notify_info(resp, f"{name} operation complete.")
            self.add_event(resp, "update-port")
            # update selector in case update selection
            self.add_event(resp, "selector")
        except (err_types.OutOfBoundsError, err_types.UserError, err_types.DoesNotExistError, err_types.InputError) as e:
            e = Exception(f"Could not apply {name} operation: {e}")
            self.notify_error(resp, e)

        # Let user perform new operation with new selections.
        bulk_editor.operations.state.reset_selections()

        bulk_editor_html = bulk_editor.render()
        resp.set_data(bulk_editor_html)
        return resp

    def toggle_viewer(self):
        resp = Response()

        show_viewer = command_palette.state.get_show_viewer()
        command_palette.state.set_show_viewer(not show_viewer)

        viewer_html = viewer.render()
        resp.set_data(viewer_html)
        return resp

    def render_cell_targeter(self):
        resp = Response()

        cell_targeter_html = viewer.target.render()
        resp.set_data(cell_targeter_html)
        return resp

    def apply_target(self):
        resp = Response()

        try:
            viewer.target.set()

            self.add_event(resp, "update-port")
        except err_types.NotSupportedError as e:
            e = Exception(f"Could not apply target: {e}")
            self.notify_error(resp, e)

        viewer_html = viewer.render()
        resp.set_data(viewer_html)
        return resp

    def move_port(self, method):
        resp = Response()

        viewer.move_upperleft(method)

        self.add_event(resp, "update-port")

        viewer_html = viewer.render()
        resp.set_data(viewer_html)
        return resp

    def update_dimensions(self, nrows, ncols):
        resp = Response()

        viewer.state.set_dimensions(nrows, ncols)

        port_html = self.render_port_helper(resp)
        resp.set_data(port_html)
        return resp
