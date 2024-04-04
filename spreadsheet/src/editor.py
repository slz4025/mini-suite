from flask import render_template

import src.errors as errors
import src.command_palette as command_palette
import src.navigator as navigator
import src.data.operations as operations
import src.selection.types as sel_types


def get_focused_cell_position(session):
    if "focused-cell-position" not in session:
        return None

    return sel_types.CellPosition(
        row_index=sel_types.RowIndex(
            int(session["focused-cell-position"]["row-index"])
        ),
        col_index=sel_types.ColIndex(
            int(session["focused-cell-position"]["col-index"])
        ),
    )


def set_focused_cell_position(session, focused_cell_position):
    session["focused-cell-position"] = {
        "row-index": str(focused_cell_position.row_index.value),
        "col-index": str(focused_cell_position.col_index.value),
    }


def reset_focused_cell_position(session):
    del session["focused-cell-position"]


def is_editing(session, cell_position):
    focused_cell_position = get_focused_cell_position(session)
    if focused_cell_position is None:
        return False
    return focused_cell_position.equals(cell_position)


def render(session):
    show_help = command_palette.get_show_help(session)
    show_editor = command_palette.get_show_editor(session)
    focused_cell = get_focused_cell_position(session)
    if focused_cell is not None:
        try:
            sel_types.check_cell_position(focused_cell)
        except errors.OutOfBoundsError:
            reset_focused_cell_position(session)
            focused_cell = None
        if not navigator.in_view(session, focused_cell):
            reset_focused_cell_position(session)
            focused_cell = None

    row = None
    col = None
    data = None
    editing = focused_cell is not None
    if editing:
        row = focused_cell.row_index.value
        col = focused_cell.col_index.value
        data = operations.get_cell_formula(focused_cell)

    return render_template(
        "partials/editor.html",
        show_help=show_help,
        show_editor=show_editor,
        editing=editing,
        row=row if row is not None else "",
        col=col if col is not None else "",
        data=data if data is not None else "",
    )
