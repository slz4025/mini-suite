from flask import render_template

import src.errors as errors
import src.modes as modes
import src.navigator as navigator
import src.data.operations as operations
import src.selection.types as sel_types
import src.settings as settings


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
    return focused_cell_position.equals(cell_position)


def in_port(session, cell_position):
    upperleft = navigator.get_upperleft(session)
    current_settings = settings.get(session)

    start_row = upperleft.row_index.value
    start_col = upperleft.col_index.value
    end_row = start_row + current_settings.nrows
    end_col = start_col + current_settings.ncols

    row = cell_position.row_index.value
    col = cell_position.col_index.value

    return (row >= start_row and row < end_row) \
        and (col >= start_col and col < end_col)


def render(session):
    editor_state = modes.check(session, "Editor")
    focused_cell = get_focused_cell_position(session)
    if focused_cell is not None:
        try:
            sel_types.check_cell_position(focused_cell)
        except errors.OutOfBoundsError:
            reset_focused_cell_position(session)
            focused_cell = None
        if not in_port(session, focused_cell):
            reset_focused_cell_position(session)
            focused_cell = None

    row = None
    col = None
    data = None
    editing = focused_cell is not None
    if editing:
        row = focused_cell.row_index.value
        col = focused_cell.col_index.value
        data = operations.get_cell(focused_cell)

    return render_template(
        "partials/editor.html",
        show_editor=editor_state,
        editing=editing,
        row=row if row is not None else "",
        col=col if col is not None else "",
        data=data if data is not None else "",
    )
