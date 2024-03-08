from dataclasses import dataclass
from typing import Union

import src.errors as errors
import src.data.sheet as sheet


class RowIndex(sheet.Index):
    def __init__(self, value):
        super().__init__(value)


class ColIndex(sheet.Index):
    def __init__(self, value):
        super().__init__(value)


@dataclass
class CellPosition:
    row_index: RowIndex
    col_index: ColIndex


class RowRange(sheet.Range):
    def __init__(self, start, end):
        super().__init__(start, end)


class ColRange(sheet.Range):
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
    bounds = sheet.get_bounds()

    if row_index.value < 0 or row_index.value > bounds.row.value:
        raise errors.OutOfBoundsError(
            f"Row index, {row_index.value}, "
            f"is out of bounds [{0}:{bounds.row.value}]."
        )


def check_col_index(col_index):
    bounds = sheet.get_bounds()

    if col_index.value < 0 or col_index.value > bounds.col.value:
        raise errors.OutOfBoundsError(
            f"Column index, {col_index.value}, "
            f"is out of bounds [{0}:{bounds.col.value}]."
        )


def check_cell_position(cell_position):
    check_row_index(cell_position.row_index)
    check_col_index(cell_position.col_index)


def check_and_set_row_range(row_range):
    bounds = sheet.get_bounds()

    if row_range.start is None:
        row_range.start = sheet.Index(0)
    if row_range.end is None:
        row_range.end = sheet.Bound(bounds.row.value)

    if row_range.start.value < 0:
        raise errors.OutOfBoundsError(
            f"Row range start, {row_range.start.value}, "
            "is negative."
        )
    if row_range.end.value > bounds.row.value:
        raise errors.OutOfBoundsError(
            f"Row range end, {row_range.end.value}, "
            f"exceeds sheet bound, {bounds.row.value}."
        )
    if row_range.start.value >= row_range.end.value:
        raise errors.OutOfBoundsError(
            f"Row range start, {row_range.start.value}, "
            "is greater than or equal to "
            f"row range end, {row_range.end.value}."
        )

    return row_range


def check_and_set_col_range(col_range):
    bounds = sheet.get_bounds()

    if col_range.start is None:
        col_range.start = sheet.Index(0)
    if col_range.end is None:
        col_range.end = sheet.Bound(bounds.col.value)

    if col_range.start.value < 0:
        raise errors.OutOfBoundsError(
            f"Column range start, {col_range.start.value}, "
            "is negative."
        )
    if col_range.end.value > bounds.col.value:
        raise errors.OutOfBoundsError(
            f"Column range end, {col_range.end.value}, "
            f"exceeds sheet bound, {bounds.col.value}."
        )
    if col_range.start.value >= col_range.end.value:
        raise errors.OutOfBoundsError(
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
