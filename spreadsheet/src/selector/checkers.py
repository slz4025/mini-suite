import src.errors.types as err_types
import src.sheet as sheet

import src.sheet.types as sheet_types

import src.selector.types as types


def check_row_index(row_index):
    bounds = sheet.data.get_bounds()

    if row_index.value < 0 or row_index.value > bounds.row.value:
        raise err_types.OutOfBoundsError(
            f"Row index, {row_index.value}, "
            f"is out of bounds [{0}:{bounds.row.value}]."
        )


def check_col_index(col_index):
    bounds = sheet.data.get_bounds()

    if col_index.value < 0 or col_index.value > bounds.col.value:
        raise err_types.OutOfBoundsError(
            f"Column index, {col_index.value}, "
            f"is out of bounds [{0}:{bounds.col.value}]."
        )


def check_cell_position(cell_position):
    check_row_index(cell_position.row_index)
    check_col_index(cell_position.col_index)


def check_and_set_row_range(row_range):
    bounds = sheet.data.get_bounds()

    if row_range.start is None:
        row_range.start = sheet_types.Index(0)
    if row_range.end is None:
        row_range.end = sheet_types.Bound(bounds.row.value)

    if row_range.start.value < 0:
        raise err_types.OutOfBoundsError(
            f"Row range start, {row_range.start.value}, "
            "is negative."
        )
    if row_range.end.value > bounds.row.value:
        raise err_types.OutOfBoundsError(
            f"Row range end, {row_range.end.value}, "
            f"exceeds sheet bound, {bounds.row.value}."
        )
    if row_range.start.value >= row_range.end.value:
        raise err_types.OutOfBoundsError(
            f"Row range start, {row_range.start.value}, "
            "is greater than or equal to "
            f"row range end, {row_range.end.value}."
        )

    return row_range


def check_and_set_col_range(col_range):
    bounds = sheet.data.get_bounds()

    if col_range.start is None:
        col_range.start = sheet_types.Index(0)
    if col_range.end is None:
        col_range.end = sheet_types.Bound(bounds.col.value)

    if col_range.start.value < 0:
        raise err_types.OutOfBoundsError(
            f"Column range start, {col_range.start.value}, "
            "is negative."
        )
    if col_range.end.value > bounds.col.value:
        raise err_types.OutOfBoundsError(
            f"Column range end, {col_range.end.value}, "
            f"exceeds sheet bound, {bounds.col.value}."
        )
    if col_range.start.value >= col_range.end.value:
        raise err_types.OutOfBoundsError(
            f"Column range start, {col_range.start.value}, "
            "is greater than or equal to "
            f"column range end, {col_range.end.value}."
        )

    return col_range


def check_and_set_box(box):
    row_range = check_and_set_row_range(box.row_range)
    col_range = check_and_set_col_range(box.col_range)

    box.row_range = row_range
    box.col_range = col_range

    return box


def check_selection(sel):
    if isinstance(sel, types.RowIndex):
        check_row_index(sel)
    elif isinstance(sel, types.ColIndex):
        check_col_index(sel)
    elif isinstance(sel, types.CellPosition):
        check_cell_position(sel)
    elif isinstance(sel, types.RowRange):
        check_and_set_row_range(sel)
    elif isinstance(sel, types.ColRange):
        check_and_set_col_range(sel)
    elif isinstance(sel, types.Box):
        check_and_set_box(sel)
    else:
        sel_type = type(sel)
        raise err_types.UnknownOptionError(
            f"Unknown selection type: {sel_type}."
        )
