import src.errors as errors
import src.selection.types as sel_types
import src.sheet as sheet

import src.computer.graph as graph


def is_formula(formula):
    return graph.is_formula(formula)


def get_cell_computed(cell_position):
    return graph.compute(cell_position)


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
