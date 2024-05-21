import numpy as np
from typing import Any, Dict

import src.errors as errors
import src.selection.types as sel_types
import src.sheet as sheet

import src.computer.graph as graph


def is_formula(formula):
    return graph.is_formula(formula)


def get_cell_computed(cell_position):
    value = graph.compute(cell_position)
    return value


def get_all_cells_computed():
    bounds = sheet.get_bounds()
    data = np.empty((bounds.row.value, bounds.col.value), dtype=object)
    for row in range(bounds.row.value):
        for col in range(bounds.col.value):
            data[row, col] = get_cell_computed(sel_types.CellPosition(
                row_index=sel_types.RowIndex(int(row)),
                col_index=sel_types.ColIndex(int(col)),
            ))
    return data


def update_cell_value(cell_position, value):
    sel_types.check_cell_position(cell_position)
    ptr = sheet.get()

    prev_value = ptr[
        cell_position.row_index.value, cell_position.col_index.value
    ]

    ptr[cell_position.row_index.value, cell_position.col_index.value] = value

    # Determine if new value is valid.
    # If not, rollback to previous value.
    try:
        graph.compute(cell_position)
    except errors.UserError as e:
        ptr[
            cell_position.row_index.value, cell_position.col_index.value
        ] = prev_value
        raise e
