from typing import Dict

import src.selector.modes as sel_modes
import src.selector.types as sel_types


current_operation = "Delete"
buffer_selection_mode = None
selections: Dict[str, sel_types.Selection] = {}


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


def set_selection(use, sel):
  global selections
  selections[use] = sel


def get_selections():
  return selections


def reset_selections():
  global selections
  selections = {}
