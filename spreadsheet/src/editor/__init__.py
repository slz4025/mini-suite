from flask import render_template

import src.errors as errors
import src.command_palette.state as cp_state
import src.port.viewer as viewer
import src.sheet as sheet
import src.selection.modes as sel_modes
import src.selection.types as sel_types

import src.editor.state as state
import src.editor.operations as operations


def render(session, op_name_str=None):
    show_help = cp_state.get_show_help(session)
    show_editor = cp_state.get_show_editor(session)

    focused_cell = state.get_focused_cell_position(session)
    if focused_cell is not None:
        try:
            sel_types.check_cell_position(focused_cell)
        except errors.OutOfBoundsError:
            state.reset_focused_cell_position(session)
            focused_cell = None

    if focused_cell is not None:
        if not viewer.in_view(session, focused_cell):
            state.reset_focused_cell_position(session)
            focused_cell = None

    row = None
    col = None
    data = None
    editing = focused_cell is not None

    if editing:
        row = focused_cell.row_index.value
        col = focused_cell.col_index.value

        if op_name_str is not None:
            op_name = operations.from_input(op_name_str)
            data = operations.get_formula_with_selection(session, op_name)
        else:
            data = sheet.get_cell_value(focused_cell)

    operations_html = operations.render(session)
    return render_template(
        "partials/editor.html",
        show_help=show_help,
        show_editor=show_editor,
        editing=editing,
        operations=operations_html,
        row=row if row is not None else "",
        col=col if col is not None else "",
        data=data if data is not None else "",
    )
