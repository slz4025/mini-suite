selection_mode = None
selection = None


def get_mode():
    return selection_mode


def set_mode(_selection_mode):
    global selection_mode
    selection_mode = _selection_mode


def reset_mode():
    global selection_mode
    selection_mode = None


def get_selection():
    return selection


def set_selection(sel):
    global selection
    selection = sel


def reset_selection():
    global selection
    selection = None
