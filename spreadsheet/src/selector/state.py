selection = None


def get_selection():
    return selection


def set_selection(sel):
    global selection
    selection = sel


def reset_selection():
    global selection
    selection = None
