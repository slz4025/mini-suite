from dataclasses import dataclass
from enum import Enum
from typing import Union

import src.errors.types as err_types
import src.sheet as sheet
import src.sheet.types as sheet_types


class Mode(Enum):
    ROW_INDEX = "Row"
    COLUMN_INDEX = "Column"
    CELL_POSITION = "Cell Position"
    ROWS = "Rows"
    COLUMNS = "Columns"
    BOX = "Box"


class RowIndex(sheet_types.Index):
    def __init__(self, value):
        super().__init__(value)


class ColIndex(sheet_types.Index):
    def __init__(self, value):
        super().__init__(value)


class CellPosition:
    def __init__(self, row_index: RowIndex, col_index: ColIndex):
        self.row_index = row_index
        self.col_index = col_index

    def equals(self, other):
        return self.row_index.equals(other.row_index) \
            and self.col_index.equals(other.col_index)

    def in_bounds(self, start_row, end_row, start_col, end_col):
        return self.row_index.in_bounds(start_row, end_row) \
            and self.col_index.in_bounds(start_col, end_col)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self.equals(other)

    def __hash__(self):
        return hash((self.row_index.value, self.col_index.value))


class RowRange(sheet_types.Range):
    def __init__(self, start, end):
        super().__init__(start, end)


class ColRange(sheet_types.Range):
    def __init__(self, start, end):
        super().__init__(start, end)


@dataclass
class Box:
    row_range: RowRange
    col_range: ColRange


Selection = Union[
    RowIndex,
    ColIndex,
    CellPosition,
    RowRange,
    ColRange,
    Box,
]


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


def get_bounds_from_selection(sel):
    row_range = check_and_set_row_range(
        RowRange(start=None, end=None),
    )
    row_start = row_range.start.value
    row_end = row_range.end.value

    col_range = check_and_set_col_range(
        ColRange(start=None, end=None),
    )
    col_start = col_range.start.value
    col_end = col_range.end.value

    if isinstance(sel, RowRange):
        row_start = sel.start.value
        row_end = sel.end.value
    elif isinstance(sel, ColRange):
        col_start = sel.start.value
        col_end = sel.end.value
    elif isinstance(sel, Box):
        row_start = sel.row_range.start.value
        row_end = sel.row_range.end.value
        col_start = sel.col_range.start.value
        col_end = sel.col_range.end.value
    else:
        raise err_types.NotSupportedError(
            f"Selection type, {type(sel)}, does not have bounds."
        )

    return row_start, row_end, col_start, col_end


def check_selection(sel):
    if isinstance(sel, RowIndex):
        check_row_index(sel)
    elif isinstance(sel, ColIndex):
        check_col_index(sel)
    elif isinstance(sel, CellPosition):
        check_cell_position(sel)
    elif isinstance(sel, RowRange):
        check_and_set_row_range(sel)
    elif isinstance(sel, ColRange):
        check_and_set_col_range(sel)
    elif isinstance(sel, Box):
        check_and_set_box(sel)
    else:
        sel_type = type(sel)
        raise err_types.UnknownOptionError(
            f"Unknown selection type: {sel_type}."
        )
