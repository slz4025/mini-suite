# Modification on the sheet itself.
# Each modification is as simple as possible.

import copy
from dataclasses import dataclass
from enum import Enum
import numpy as np
from typing import Callable, Union

import src.errors.types as err_types
import src.selector.types as sel_types
import src.sheet.data as sheet_data


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


def apply_delete(sel):
    start = None
    end = None
    axis = None

    if isinstance(sel, sel_types.RowRange):
        start = sel.start.value
        end = sel.end.value
        axis = Axis.ROW
    elif isinstance(sel, sel_types.ColRange):
        start = sel.start.value
        end = sel.end.value
        axis = Axis.COLUMN
    else:
        raise err_types.NotSupportedError(
            f"Option {type(sel)} is not valid for delete."
        )

    assert start is not None
    assert end is not None
    assert axis is not None

    ptr = sheet_data.get()
    indices = list(range(start, end))
    sheet_data.set(np.delete(ptr, indices, axis.value))


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
        raise err_types.NotSupportedError(
            f"Option, {type(sel)}, is not valid for insert."
        )

    assert index is not None
    assert axis is not None

    ptr = sheet_data.get()
    number = inp.number
    insertion = np.array([[None] * number])
    sheet_data.set(np.insert(
        ptr,
        [index] * number,
        insertion if axis == Axis.COLUMN else insertion.T,
        axis=axis.value,
    ))


def apply_value(inp):
    sel = inp.selection
    row_start, row_end, col_start, col_end = \
        sel_types.get_bounds_from_selection(sel)

    value = inp.value
    ptr = sheet_data.get()
    ptr[row_start:row_end, col_start:col_end] = value


buffer = None


def apply_copy(sel):
    global buffer

    row_start, row_end, col_start, col_end = \
        sel_types.get_bounds_from_selection(sel)

    ptr = sheet_data.get()
    buffer = copy.deepcopy(ptr[row_start:row_end, col_start:col_end])


def maybe_insert_at_end(axis, needed):
    bounds = sheet_data.get_bounds()
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
        raise err_types.UserError("Nothing in buffer to paste from.")

    # Copy objects, e.g. strings, within the array.
    copied_buffer = copy.deepcopy(buffer)

    if isinstance(sel, sel_types.RowIndex):
        row_start = sel.value
        row_end = row_start + copied_buffer.shape[0]
        col_start = 0
        col_end = copied_buffer.shape[1]
        assert col_end == sheet_data.get_bounds().col.value
    elif isinstance(sel, sel_types.ColIndex):
        row_start = 0
        row_end = copied_buffer.shape[0]
        assert row_end == sheet_data.get_bounds().row.value
        col_start = sel.value
        col_end = col_start + copied_buffer.shape[1]
    elif isinstance(sel, sel_types.CellPosition):
        row_start = sel.row_index.value
        row_end = row_start + copied_buffer.shape[0]
        col_start = sel.col_index.value
        col_end = col_start + copied_buffer.shape[1]
    else:
        raise err_types.NotSupportedError(
            f"Option, {type(sel)}, is not valid for paste."
        )

    maybe_insert_at_end(Axis.ROW, row_end)
    maybe_insert_at_end(Axis.COLUMN, col_end)

    ptr = sheet_data.get()
    ptr[row_start:row_end, col_start:col_end] = copied_buffer


class Type(Enum):
    DELETE = 'DELETE'
    INSERT = 'INSERT'
    VALUE = 'VALUE'
    COPY = 'COPY'
    PASTE = 'PASTE'


@dataclass
class Operation:
    name: Type
    apply: Callable[[Input], None]


operations = {
    Type.DELETE: Operation(name=Type.DELETE, apply=apply_delete),
    Type.INSERT: Operation(name=Type.INSERT, apply=apply_insert),
    Type.VALUE: Operation(name=Type.VALUE, apply=apply_value),
    Type.COPY: Operation(name=Type.COPY, apply=apply_copy),
    Type.PASTE: Operation(name=Type.PASTE, apply=apply_paste),
}


@dataclass
class Modification:
    operation: Type
    input: Input


def apply_modification(modification):
    inp = modification.input
    op_name = modification.operation
    operation = operations[op_name]
    operation.apply(inp)
