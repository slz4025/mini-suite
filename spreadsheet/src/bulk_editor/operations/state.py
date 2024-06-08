import src.bulk_editor.operations.types as types


current_operation = types.Name.INSERT_END_ROWS


def set_current_operation(op):
  global current_operation
  current_operation = op


def get_current_operation():
  return current_operation
