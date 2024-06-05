import src.selector.types as sel_types


focused_cell_position = None


def get_focused_cell_position():
    return focused_cell_position


def set_focused_cell_position(_focused_cell_position):
    global focused_cell_position
    focused_cell_position = _focused_cell_position


def reset_focused_cell_position():
    global focused_cell_position
    focused_cell_position = None
