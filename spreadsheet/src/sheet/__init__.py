import numpy as np

import src.errors.types as err_types
import src.viewer as viewer
import src.selector.types as sel_types

import src.sheet.compiler as compiler
import src.sheet.data as sheet_data
import src.sheet.files as files
import src.sheet.graph as graph
import src.sheet.types as sheet_types


# This dynamically computes cells when they are in view or are updated.
# In computing a cell, we therefore always compute its dependencies.
# In updating a cell, we must recompute its dependents, which are
# likely to have different values. Since our current sheet data structure,
# a numpy array of underlying values, does not easily allow for computation
# of dependents, we just end up recomputing all viewable cells that are
# likely to depend on the updated cell, or all viewable formulas.
#
# This method is therefore not efficient for a sheet with lots of
# computationally-expensive, deeply nested, multi-dependency formulas.
# However, we are operating under the assumption that this tool will
# mainly be used for managing tabular data and simple formulas.
# Given a reasonably sized port, fetches should still have minimal latency.
#
# If this assumption changes, we can consider using a data structure,
# like an array of objects that store the underlying value, pointers
# to the dependencies, pointers to the  dependents, and computed value.
# This data structure has the following advantages:
# - caching of cell values, allowing fetches to be fast,
# - more efficient updating of the DAG of cell dependencies when a single
#   cell or group of cells change,
# - efficient modification to the sheet when inserting or deleting rows
#   and columns.
# Initialization of the cache can take place when first importing the
# spreadsheet or at the time of load, the latter likely being better
# if the spreadsheet is large and complicated.


def is_markdown(cell_position):
    underlying_value = sheet_data.get_cell_value(cell_position)
    return graph.is_markdown(underlying_value)


def get_cell_computed(cell_position):
    value = graph.compute(cell_position)
    return value


def get_all_cells_computed():
    bounds = sheet_data.get_bounds()
    data = np.empty((bounds.row.value, bounds.col.value), dtype=object)
    for row in range(bounds.row.value):
        for col in range(bounds.col.value):
            data[row, col] = get_cell_computed(sel_types.CellPosition(
                row_index=sel_types.RowIndex(int(row)),
                col_index=sel_types.ColIndex(int(col)),
            ))
    return data


def get_cells_containing_text(text):
    relevant = []

    computed_data = get_all_cells_computed()
    for row in range(computed_data.shape[0]):
        for col in range(computed_data.shape[1]):
            computed = computed_data[row, col]
            if isinstance(computed, str) and text in computed:
                pos = sel_types.CellPosition(
                    row_index=sel_types.RowIndex(int(row)),
                    col_index=sel_types.ColIndex(int(col)),
                )
                relevant.append(pos)
    return relevant


def get_potential_dependents():
    upperleft = viewer.state.get_upperleft()
    nrows, ncols = viewer.state.get_dimensions()
    bounds = sheet_data.get_bounds()

    viewable_formulas = []
    for row in range(
        upperleft.row_index.value,
        min(upperleft.row_index.value+nrows, bounds.row.value)
    ):
        for col in range(
            upperleft.col_index.value,
            min(upperleft.col_index.value+ncols, bounds.col.value)
        ):
            cell_position = sel_types.CellPosition(
                row_index=sel_types.RowIndex(row),
                col_index=sel_types.ColIndex(col),
            )
            value = sheet_data.get_cell_value(cell_position)
            if graph.is_formula(value):
                viewable_formulas.append(cell_position)
    return viewable_formulas


def update_cell_value(cell_position, value):
    sel_types.check_cell_position(cell_position)
    ptr = sheet_data.get()

    prev_value = ptr[
        cell_position.row_index.value, cell_position.col_index.value
    ]

    compiled_value = compiler.user_string_to_value(value)
    ptr[cell_position.row_index.value, cell_position.col_index.value] = compiled_value

    # Determine if new value is valid.
    # If not, rollback to previous value.
    try:
        graph.compute(cell_position)
    except err_types.UserError as e:
        ptr[
            cell_position.row_index.value, cell_position.col_index.value
        ] = prev_value
        raise e
