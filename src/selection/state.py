import jsonpickle

import src.selection.modes as modes


def get_mode(session):
    if "selection-mode" not in session:
        return None
    mode_str = session["selection-mode"]
    mode = modes.from_input(mode_str)
    return mode


def set_mode(session, mode):
    session["selection-mode"] = mode.value


def get_buffer_mode(session):
    if "buffer-selection-mode" not in session:
        return None
    mode_str = session["buffer-selection-mode"]
    mode = modes.from_input(mode_str)
    return mode


def set_buffer_mode(session, sel):
    mode = modes.from_selection(sel)
    session["buffer-selection-mode"] = mode.value


def get_selection(session):
    if "selection" not in session:
        return None
    pickled = session["selection"]
    sel = jsonpickle.decode(pickled)
    return sel


def set_selection(session, sel):
    pickled = jsonpickle.encode(sel)
    session["selection"] = pickled
