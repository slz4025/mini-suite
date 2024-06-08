import src.selector.modes as modes


selection_mode = None
selection = None
buffer_selection_mode = None


def get_mode():
    return selection_mode


def set_mode(_selection_mode):
    global selection_mode
    selection_mode = _selection_mode


def reset_mode():
    global selection_mode
    selection_mode = None


def get_buffer_mode():
    return buffer_selection_mode


def set_buffer_mode(sel):
    global buffer_selection_mode
    mode = modes.from_selection(sel)
    buffer_selection_mode = mode


def get_selection():
    return selection


def set_selection(sel):
    global selection
    selection = sel


def reset_selection():
    global selection
    selection = None
