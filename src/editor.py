from flask import render_template

import src.modes as modes
import src.data.operations as operations
import src.selection.types as sel_types


def get_focused_cell_position(session):
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


def is_editing(session, cell_position):
    focused_cell_position = get_focused_cell_position(session)
    return focused_cell_position.equals(cell_position)


def render(session):
    editor_state = modes.check(session, "Editor")
    focused_cell = get_focused_cell_position(session)
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


def init(session):
    focused_cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(0),
        col_index=sel_types.ColIndex(0),
    )
    set_focused_cell_position(session, focused_cell_position)
