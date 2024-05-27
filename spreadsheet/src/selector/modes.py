from enum import Enum

import src.errors as errors
import src.selector.types as types


class Mode(Enum):
    ROW_INDEX = "Row"
    COLUMN_INDEX = "Column"
    CELL_POSITION = "Cell Position"
    ROWS = "Rows"
    COLUMNS = "Columns"
    BOX = "Box"


def from_selection(sel):
    if isinstance(sel, types.RowIndex):
        return Mode.ROW_INDEX
    elif isinstance(sel, types.ColIndex):
        return Mode.COLUMN_INDEX
    elif isinstance(sel, types.CellPosition):
        return Mode.CELL_POSITION
    elif isinstance(sel, types.RowRange):
        return Mode.ROWS
    elif isinstance(sel, types.ColRange):
        return Mode.COLUMNS
    elif isinstance(sel, types.Box):
        return Mode.BOX
    else:
        sel_type = type(sel)
        raise errors.UnknownOptionError(
            f"Unknown selection type: {sel_type}."
        )


def from_input(mode_str):
    match mode_str:
        case "Row":
            return Mode.ROW_INDEX
        case "Column":
            return Mode.COLUMN_INDEX
        case "Cell Position":
            return Mode.CELL_POSITION
        case "Rows":
            return Mode.ROWS
        case "Columns":
            return Mode.COLUMNS
        case "Box":
            return Mode.BOX
        case _:
            raise errors.UnknownOptionError(
                f"Unknown selection mode: {mode_str}."
            )
