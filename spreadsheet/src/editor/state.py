import src.selection.types as sel_types


# The focused cell is the cell that displays its underlying value.


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
