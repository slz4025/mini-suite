from typing import Dict

import src.selector.types as sel_types


current_operation = "Delete"
buffer_selection_type = None
selections: Dict[str, sel_types.Selection] = {}


def set_current_operation(op):
    global current_operation
    current_operation = op


def get_current_operation():
    return current_operation


def get_buffer_type():
    return buffer_selection_type


def set_buffer_type(sel):
    global buffer_selection_type
    buffer_selection_type = type(sel)


def set_selection(use, sel):
  global selections
  selections[use] = sel


def get_selections():
  return selections


def reset_selections():
  global selections
  selections = {}
