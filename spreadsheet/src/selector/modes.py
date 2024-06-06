import src.errors.types as err_types

import src.selector.types as types


def from_selection(sel):
    if isinstance(sel, types.RowIndex):
        return types.Mode.ROW_INDEX
    elif isinstance(sel, types.ColIndex):
        return types.Mode.COLUMN_INDEX
    elif isinstance(sel, types.CellPosition):
        return types.Mode.CELL_POSITION
    elif isinstance(sel, types.RowRange):
        return types.Mode.ROWS
    elif isinstance(sel, types.ColRange):
        return types.Mode.COLUMNS
    elif isinstance(sel, types.Box):
        return types.Mode.BOX
    else:
        sel_type = type(sel)
        raise err_types.UnknownOptionError(
            f"Unknown selection type: {sel_type}."
        )


def from_input(mode_str):
    match mode_str:
        case "Row":
            return types.Mode.ROW_INDEX
        case "Column":
            return types.Mode.COLUMN_INDEX
        case "Cell Position":
            return types.Mode.CELL_POSITION
        case "Rows":
            return types.Mode.ROWS
        case "Columns":
            return types.Mode.COLUMNS
        case "Box":
            return types.Mode.BOX
        case _:
            raise err_types.UnknownOptionError(
                f"Unknown selection mode: {mode_str}."
            )
