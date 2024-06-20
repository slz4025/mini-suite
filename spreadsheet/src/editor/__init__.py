from flask import render_template

import src.errors.types as err_types
import src.command_palette as command_palette
import src.viewer as viewer
import src.selector.checkers as sel_checkers
import src.sheet as sheet

import src.editor.state as state
import src.editor.operations as operations


def is_editing(cell_position):
    focused_cell_position = state.get_focused_cell_position()
    if focused_cell_position is None:
        return False
    return focused_cell_position.equals(cell_position)


def render(op_name=None):
    show_help = command_palette.state.get_show_help()
    show_editor = command_palette.state.get_show_editor()

    focused_cell = state.get_focused_cell_position()
    if focused_cell is not None:
        try:
            sel_checkers.check_cell_position(focused_cell)
        except err_types.OutOfBoundsError:
            state.reset_focused_cell_position()
            focused_cell = None

    if focused_cell is not None:
        if not viewer.in_view(focused_cell):
            state.reset_focused_cell_position()
            focused_cell = None

    row = None
    col = None
    data = None
    editing = focused_cell is not None

    if editing:
        row = focused_cell.row_index.value
        col = focused_cell.col_index.value

        if op_name is not None:
            data = operations.get_value(op_name)
        else:
            data = sheet.data.get_cell_value(focused_cell)

    operations_html = operations.render()
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
