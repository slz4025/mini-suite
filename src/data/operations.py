import copy
from dataclasses import dataclass
from enum import Enum
import numpy as np
from typing import Callable, Union

import src.errors as errors

import src.data.sheet as sheet
import src.selection.types as sel_types


class Axis(Enum):
    ROW = 0
    COLUMN = 1


@dataclass
class InsertInput:
    selection: sel_types.RowIndex | sel_types.ColIndex
    number: int


@dataclass
class ValueInput:
    selection: sel_types.RowRange \
        | sel_types.ColRange \
        | sel_types.Box
    value: object


Input = Union[InsertInput, ValueInput, sel_types.Selection]


def get_cell(cell_position):
    ptr = sheet.get()
    return ptr[cell_position.row_index.value, cell_position.col_index.value]


def update_cell(cell_position, value):
    sel_types.check_cell_position(cell_position)
    ptr = sheet.get()
    ptr[cell_position.row_index.value, cell_position.col_index.value] = value


def apply_delete(sel):
    start = None
    end = None
    axis = None

    if isinstance(sel, sel_types.RowIndex):
        start = sel.value
        end = start+1
        axis = Axis.ROW
    elif isinstance(sel, sel_types.ColIndex):
        start = sel.value
        end = start+1
        axis = Axis.COLUMN
    elif isinstance(sel, sel_types.RowRange):
        start = sel.start.value
        end = sel.end.value
        axis = Axis.ROW
    elif isinstance(sel, sel_types.ColRange):
        start = sel.start.value
        end = sel.end.value
        axis = Axis.COLUMN
    else:
        raise errors.UnknownOptionError(
            f"Option {type(sel)} is not valid for delete."
        )

    assert start is not None
    assert end is not None
    assert axis is not None

    ptr = sheet.get()
    indices = list(range(start, end))
    sheet.set(np.delete(ptr, indices, axis.value))


def apply_insert(inp):
    index = None
    axis = None

    sel = inp.selection
    if isinstance(sel, sel_types.RowIndex):
        index = sel.value
        axis = Axis.ROW
    elif isinstance(sel, sel_types.ColIndex):
        index = sel.value
        axis = Axis.COLUMN
    else:
        raise errors.UnknownOptionError(
            f"Option, {type(sel)}, is not valid for insert."
        )

    assert index is not None
    assert axis is not None

    ptr = sheet.get()
    number = inp.number
    insertion = np.array([[None] * number])
    sheet.set(np.insert(
        ptr,
        [index] * number,
        insertion if axis == Axis.COLUMN else insertion.T,
        axis=axis.value,
    ))


def get_bounds_from_selection(sel):
    row_range = sel_types.check_and_set_row_range(
        sel_types.RowRange(start=None, end=None),
    )
    row_start = row_range.start.value
    row_end = row_range.end.value

    col_range = sel_types.check_and_set_col_range(
        sel_types.ColRange(start=None, end=None),
    )
    col_start = col_range.start.value
    col_end = col_range.end.value

    if isinstance(sel, sel_types.RowRange):
        row_start = sel.start.value
        row_end = sel.end.value
    elif isinstance(sel, sel_types.ColRange):
        col_start = sel.start.value
        col_end = sel.end.value
    elif isinstance(sel, sel_types.Box):
        row_start = sel.row_range.start.value
        row_end = sel.row_range.end.value
        col_start = sel.col_range.start.value
        col_end = sel.col_range.end.value
    else:
        raise errors.UnknownOptionError(
            f"Option, {type(sel)}, is not valid."
        )

    return row_start, row_end, col_start, col_end


def apply_value(inp):
    sel = inp.selection
    row_start, row_end, col_start, col_end = get_bounds_from_selection(sel)

    value = inp.value
    ptr = sheet.get()
    ptr[row_start:row_end, col_start:col_end] = value


def apply_erase(sel):
    inp = ValueInput(selection=sel, value=None)
    apply_value(inp)


buffer = None


def apply_copy(sel):
    global buffer

    row_start, row_end, col_start, col_end = get_bounds_from_selection(sel)

    ptr = sheet.get()
    buffer = copy.deepcopy(ptr[row_start:row_end, col_start:col_end])


def maybe_insert_at_end(axis, needed):
    bounds = sheet.get_bounds()
    match axis:
        case Axis.ROW:
            bound = bounds.row.value
            selection = sel_types.RowIndex(bound)
        case Axis.COLUMN:
            bound = bounds.col.value
            selection = sel_types.ColIndex(bound)

    number = needed - bound
    if number > 0:
        apply_insert(InsertInput(
            selection=selection,
            number=number,
        ))


def apply_paste(sel):
    if buffer is None:
        raise errors.UserError("Nothing in buffer to paste from.")

    # Copy objects, e.g. strings, within the array.
    copied_buffer = copy.deepcopy(buffer)

    if isinstance(sel, sel_types.RowIndex):
        row_start = sel.value
        row_end = row_start + copied_buffer.shape[0]
        col_start = 0
        col_end = copied_buffer.shape[1]
        assert col_end == sheet.get_bounds().col.value
    elif isinstance(sel, sel_types.ColIndex):
        row_start = 0
        row_end = copied_buffer.shape[0]
        assert row_end == sheet.get_bounds().row.value
        col_start = sel.value
        col_end = col_start + copied_buffer.shape[1]
    elif isinstance(sel, sel_types.CellPosition):
        row_start = sel.row_index.value
        row_end = row_start + copied_buffer.shape[0]
        col_start = sel.col_index.value
        col_end = col_start + copied_buffer.shape[1]
    else:
        raise errors.UnknownOptionError(
            f"Option, {type(sel)}, is not valid."
        )

    maybe_insert_at_end(Axis.ROW, row_end)
    maybe_insert_at_end(Axis.COLUMN, col_end)

    ptr = sheet.get()
    ptr[row_start:row_end, col_start:col_end] = copied_buffer


@dataclass
class Operation:
    name: str
    apply: Callable[[Input], None]


operations = {
    "DELETE": Operation(name="DELETE", apply=apply_delete),
    "INSERT": Operation(name="INSERT", apply=apply_insert),
    "ERASE": Operation(name="ERASE", apply=apply_erase),
    "VALUE": Operation(name="VALUE", apply=apply_value),
    "COPY": Operation(name="COPY", apply=apply_copy),
    "PASTE": Operation(name="PASTE", apply=apply_paste),
}


@dataclass
class Modification:
    operation: Operation
    input: Input


def apply_modification(modification):
    global sheet

    inp = modification.input
    op_name = modification.operation
    operation = operations[op_name]
    operation.apply(inp)
