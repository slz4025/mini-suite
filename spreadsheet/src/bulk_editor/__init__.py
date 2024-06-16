from flask import render_template

import src.command_palette as command_palette
import src.errors.types as err_types
import src.selector.state as sel_state
import src.selector.types as sel_types
import src.sheet as sheet

import src.bulk_editor.operations as operations


def render():
    show_help = command_palette.state.get_show_help()
    show_bulk_editor = command_palette.state.get_show_bulk_editor()

    options = operations.get_options()
    op_name = operations.state.get_current_operation()
    operation_html = operations.render(op_name)

    return render_template(
            "partials/bulk_editor.html",
            show_help=show_help,
            show_bulk_editor=show_bulk_editor,
            operation=op_name,
            operation_options=options,
            operation_html=operation_html,
    )


def apply(name, form):
    operations.apply(name, form)


def get_shortcut_inputs(shortcut):
    name = None
    form = None
    sels = None
    match shortcut:
        case "Cut":
            name = "Cut"
            form = None
            selection = sel_state.get_selection()
            sels = {"input": selection}
        case "Copy":
            name = "Copy"
            form = None
            selection = sel_state.get_selection()
            sels = {"input": selection}
        case "Paste":
            name = "Paste"
            form = None
            selection = sel_state.get_selection()
            sels = {"target": selection}
        case "Sort":
            name = "Sort"
            form = None
            selection = sel_state.get_selection()
            sels = {"target": selection}
        case "Reverse":
            name = "Reverse"
            form = None
            sels = {}
        case "Insert":
            name = "Insert"
            form = {"insert-number": "1"}
            selection = sel_state.get_selection()
            sels = {"target": selection}
        case "Delete":
            name = "Delete"
            form = None
            selection = sel_state.get_selection()
            sels = {"input": selection}
        case "Move Forward":
            name = "Move"
            form = None
            selection = sel_state.get_selection()
            sels = {"input": selection}

            bounds = sheet.data.get_bounds()

            target = None
            if selection is not None:
                if isinstance(selection, sel_types.RowRange):
                    new_pos = selection.end.value + 1
                    if new_pos > bounds.row.value:
                        raise err_types.UserError("Cannot move rows forward anymore.")
                    target = sel_types.RowIndex(new_pos)
                elif isinstance(selection, sel_types.ColRange):
                    new_pos = selection.end.value + 1
                    if new_pos > bounds.col.value:
                        raise err_types.UserError("Cannot move columns forward anymore.")
                    target = sel_types.ColIndex(new_pos)
            sels["target"] = target
        case "Move Backward":
            name = "Move"
            form = None
            selection = sel_state.get_selection()
            sels = {"input": selection}

            bounds = sheet.data.get_bounds()

            target = None
            if selection is not None:
                if isinstance(selection, sel_types.RowRange):
                    new_pos = selection.start.value - 1
                    if new_pos < 0:
                        raise err_types.UserError("Cannot move rows backward anymore.")
                    target = sel_types.RowIndex(new_pos)
                elif isinstance(selection, sel_types.ColRange):
                    new_pos = selection.start.value - 1
                    if new_pos < 0:
                        raise err_types.UserError("Cannot move columns backward anymore.")
                    target = sel_types.ColIndex(new_pos)
            sels["target"] = target
        case "Insert End Rows":
            name = "Insert"
            form = {"insert-number": "1"}
            bounds = sheet.data.get_bounds()
            target = sel_types.RowIndex(bounds.row.value)
            sels = {"target": target}
        case "Insert End Columns":
            name = "Insert"
            form = {"insert-number": "1"}
            bounds = sheet.data.get_bounds()
            target = sel_types.ColIndex(bounds.col.value)
            sels = {"target": target}
        case _:
            raise err_types.UnknownOptionError(
                f"Unknown bulk-editor shortcut {shortcut}."
            )

    return name, form, sels
