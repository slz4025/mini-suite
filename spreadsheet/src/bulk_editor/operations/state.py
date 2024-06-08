import src.selector.modes as sel_modes

import src.bulk_editor.operations.types as types


current_operation = types.Name.INSERT_END_ROWS
buffer_selection_mode = None


def set_current_operation(op):
  global current_operation
  current_operation = op


def get_current_operation():
  return current_operation


def get_buffer_mode():
    return buffer_selection_mode


def set_buffer_mode(sel):
    global buffer_selection_mode
    mode = sel_modes.from_selection(sel)
    buffer_selection_mode = mode
