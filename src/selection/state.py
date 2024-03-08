import jsonpickle

import src.errors as errors
import src.selection.types as types


def get_mode(session):
    if "selection-mode" not in session:
        return None
    return session["selection-mode"]


def set_mode(session, mode):
    session["selection-mode"] = mode


def get_buffer_mode(session):
    if "buffer-selection-mode" not in session:
        return None
    return session["buffer-selection-mode"]


def set_buffer_mode(session, sel):
    mode = None
    if isinstance(sel, types.RowIndex):
        mode = "Row"
    elif isinstance(sel, types.ColIndex):
        mode = "Column"
    elif isinstance(sel, types.CellPosition):
        mode = "Cell Position"
    elif isinstance(sel, types.RowRange):
        mode = "Rows"
    elif isinstance(sel, types.ColRange):
        mode = "Columns"
    elif isinstance(sel, types.Box):
        mode = "Box"
    else:
        input_type = type(sel)
        raise errors.UnknownOptionError(
            f"Unexpected type {input_type} is not valid copy input."
        )

    assert mode is not None
    session["buffer-selection-mode"] = mode


def get_selection(session):
    if "selection" not in session:
        return None
    pickled = session["selection"]
    sel = jsonpickle.decode(pickled)
    return sel


def set_selection(session, sel):
    pickled = jsonpickle.encode(sel)
    session["selection"] = pickled
