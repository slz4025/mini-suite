from dataclasses import dataclass
import numpy as np
from typing import Callable, List, Optional, Union

from src.types import Index


sheet = None


@dataclass
class Range:
    start: Optional[int]
    end: Optional[int]


def set_range(axis, r):
    bounds = get_bounds()

    if axis == 0:
        start = 0 if r.start is None else r.start
        end = bounds.row if r.end is None else r.end
    if axis == 1:
        start = 0 if r.start is None else r.start
        end = bounds.col if r.end is None else r.end

    assert start is not None
    assert end is not None

    return start, end


def get_indices(start, end):
    return list(range(start, end))


@dataclass
class BoxSelection:
    rows: Range
    cols: Range


@dataclass
class RangeSelection:
    axis: int  # 0 or 1
    range: Range


@dataclass
class IndicesSelection:
    axis: int  # 0 or 1
    indices: List[int]


Selection = Union[BoxSelection, RangeSelection, IndicesSelection]


@dataclass
class InsertInput:
    axis: int
    index: int
    number: int


@dataclass
class ValueInput:
    selection: Selection
    value: object


Input = Union[InsertInput, ValueInput, Selection]


def apply_delete(sel):
    global sheet

    if isinstance(sel, RangeSelection):
        start, end = set_range(sel.axis, sel.range)
        indices = get_indices(start, end)
        sheet = np.delete(sheet, indices, sel.axis)
    elif isinstance(sel, IndicesSelection):
        sheet = np.delete(sheet, sel.indices, sel.axis)


def apply_insert(inp):
    global sheet

    insertion = np.array([[None] * inp.number])
    sheet = np.insert(
        sheet,
        [inp.index] * inp.number,
        insertion if inp.axis == 1 else insertion.T,
        axis=inp.axis,
    )


def apply_value(inp):
    global sheet

    sel = inp.selection
    value = inp.value

    if isinstance(sel, BoxSelection):
        row_start, row_end = set_range(0, sel.rows)
        col_start, col_end = set_range(0, sel.cols)
        sheet[row_start:row_end, col_start:col_end] = value
    elif isinstance(sel, RangeSelection):
        start, end = set_range(sel.axis, sel.range)
        if sel.axis == 0:
            sheet[start:end, :] = value
        if sel.axis == 1:
            sheet[:, start:end] = value
    elif isinstance(sel, IndicesSelection):
        for i in sel.indices:
            if sel.axis == 0:
                sheet[i, :] = value
            if sel.axis == 1:
                sheet[:, i] = value


def apply_erase(sel):
    inp = ValueInput(selection=sel, value=None)
    apply_value(inp)


@dataclass
class Operation:
    name: str
    apply: Callable[[Input], None]


operations = {
    "DELETE": Operation(name="DELETE", apply=apply_delete),
    "INSERT": Operation(name="INSERT", apply=apply_insert),
    "ERASE": Operation(name="ERASE", apply=apply_erase),
    "VALUE": Operation(name="VALUE", apply=apply_value),
}


@dataclass
class Modification:
    operation: Operation
    input: Input


def init_sheet(debug=False):
    global sheet

    maxrows = 100
    maxcols = 100

    sheet = np.empty((maxrows, maxcols), dtype=object)
    if debug:
        for row in range(maxrows):
            for col in range(maxcols):
                sheet[row, col] = f"{row}x{col}"


def get_value(row, col):
    return sheet[row, col]


def get_bounds():
    return Index(row=sheet.shape[0], col=sheet.shape[1])


def get_sheet():
    return sheet


def check_index(index):
    maxindex = get_bounds()
    if (index.row < 0 or index.row >= maxindex.row) \
            or (index.col < 0 or index.col >= maxindex.col):
        raise Exception(
            f"Cell index ({index.row},{index.col}) "
            f"is out of bounds ({0}:{maxindex.row},{0}:{maxindex.col})."
        )


def get_cell(index):
    check_index(index)
    return sheet[index.row, index.col]


def update_cell(index, value):
    check_index(index)
    sheet[index.row, index.col] = value


def apply_modification(modification):
    global sheet

    inp = modification.input
    op_name = modification.operation
    operation = operations[op_name]
    operation.apply(inp)
