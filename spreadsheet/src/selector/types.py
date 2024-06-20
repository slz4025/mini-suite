from dataclasses import dataclass
from typing import Union

import src.sheet.types as sheet_types


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
