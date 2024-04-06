from typing import Set

import src.errors as errors
import src.data.computer as computer
import src.data.sheet as sheet
import src.selection.types as sel_types


def get_cell_formula(cell_position):
    ptr = sheet.get()
    return ptr[cell_position.row_index.value, cell_position.col_index.value]


# This function should not be called on the same
# position more than once within a call-stack.
# If it is, this indicates a dependency loop.
visited: Set[sel_types.CellPosition] = set()


def _get_cell_value(cell_position):
    global visited

    if cell_position in visited:
        raise errors.UserError(
            "Dependency loop in computing cell values. "
            "Cell at position ("
            f"{cell_position.row_index.value},"
            f"{cell_position.col_index.value}"
            ") visited more than once."
        )

    formula = get_cell_formula(cell_position)

    visited.add(cell_position)
    value = computer.compute(cell_position, formula)
    visited.remove(cell_position)

    return value


def get_row_range_values(sel):
    sel = sel_types.check_and_set_row_range(sel)
    bounds = sheet.get_bounds()

    arr = []
    for i in range(sel.start.value, sel.end.value):
        for j in range(0, bounds.col.value):
            arr.append(_get_cell_value(sel_types.CellPosition(
                row_index=sel_types.RowIndex(i),
                col_index=sel_types.ColIndex(j),
            )))
    return arr


def get_col_range_values(sel):
    sel = sel_types.check_and_set_col_range(sel)
    bounds = sheet.get_bounds()

    arr = []
    for i in range(0, bounds.row.value):
        for j in range(sel.start.value, sel.end.value):
            arr.append(_get_cell_value(sel_types.CellPosition(
                row_index=sel_types.RowIndex(i),
                col_index=sel_types.ColIndex(j),
            )))
    return arr


def get_box_values(sel):
    sel = sel_types.check_and_set_box(sel)

    arr = []
    for i in range(sel.row_range.start.value, sel.row_range.end.value):
        for j in range(sel.col_range.start.value, sel.col_range.end.value):
            arr.append(_get_cell_value(sel_types.CellPosition(
                row_index=sel_types.RowIndex(i),
                col_index=sel_types.ColIndex(j),
            )))
    return arr


def get_cell_value(cell_position):
    # reset call stack
    global visited
    visited = set()

    return _get_cell_value(cell_position)


def update_cell(cell_position, value):
    sel_types.check_cell_position(cell_position)
    ptr = sheet.get()

    prev_value = ptr[
        cell_position.row_index.value, cell_position.col_index.value
    ]

    ptr[cell_position.row_index.value, cell_position.col_index.value] = value

    # Determine if new value is valid.
    # If not, rollback to previous value.
    try:
        get_cell_value(cell_position)
    except errors.UserError as e:
        ptr[
            cell_position.row_index.value, cell_position.col_index.value
        ] = prev_value
        raise e
