from flask import render_template

import src.command_palette as command_palette
import src.errors.types as err_types
import src.utils.form as form_helpers
import src.selector.modes as sel_modes
import src.selector.state as sel_state
import src.selector.types as sel_types
import src.sheet as sheet
import src.sheet.types as sheet_types

import src.bulk_editor.modifications as modifications
import src.bulk_editor.operations.state as state
import src.bulk_editor.operations.types as types


def add_selection(use):
    sel = sel_state.get_selection()
    state.add_selection(use, sel)


def render_use_selection(op, use):
    sel = sel_state.get_selection()
    disable = sel is None
    selections = state.get_selections()

    message = "Input Selection"
    if use in selections:
      message = "✓ Selection Inputted"
    else:
      message = "Input Selection"

    return render_template(
            "partials/bulk_editor/use_selection.html",
            op=op,
            use=use,
            disable=disable,
            message=message,
    )


def from_input(name_str):
    match name_str:
        case "Cut":
            return types.Name.CUT
        case "Copy":
            return types.Name.COPY
        case "Paste":
            return types.Name.PASTE
        case "Delete":
            return types.Name.DELETE
        case "Move":
            return types.Name.MOVE
        case "Insert":
            return types.Name.INSERT
        case "Erase":
            return types.Name.ERASE
        case "Value":
            return types.Name.VALUE
        case "Move Forward":
            return types.Name.MOVE_FORWARD
        case "Move Backward":
            return types.Name.MOVE_BACKWARD
        case "Insert End Rows":
            return types.Name.INSERT_END_ROWS
        case "Insert End Columns":
            return types.Name.INSERT_END_COLS
        case _:
            raise err_types.UnknownOptionError(
                f"Unknown operation: {name_str}."
            )


def validate_and_parse_cut(sels, form):
    if "default" not in sels:
        raise err_types.DoesNotExistError("Selection does not exist.")
    sel = sels["default"]
    sel_types.check_selection(sel)

    sel_mode = sel_modes.from_selection(sel)
    selection_mode_options = [
        sel_types.Mode.ROWS,
        sel_types.Mode.COLUMNS,
        sel_types.Mode.BOX,
    ]
    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode.value} "
            "is not supported with cut operation."
        )

    mods = []

    modification = modifications.Modification(
        operation=modifications.Type.COPY,
        input=sel,
    )
    mods.append(modification)

    inp = modifications.ValueInput(selection=sel, value=None)
    modification = modifications.Modification(
        operation=modifications.Type.VALUE,
        input=inp,
    )
    mods.append(modification)

    return mods


def validate_and_parse_copy(sels, form):
    if "default" not in sels:
        raise err_types.DoesNotExistError("Selection does not exist.")
    sel = sels["default"]
    sel_types.check_selection(sel)

    sel_mode = sel_modes.from_selection(sel)
    selection_mode_options = [
        sel_types.Mode.ROWS,
        sel_types.Mode.COLUMNS,
        sel_types.Mode.BOX,
    ]
    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode.value} "
            "is not supported with copy operation."
        )

    modification = modifications.Modification(
        operation=modifications.Type.COPY,
        input=sel,
    )
    return [modification]


def validate_and_parse_paste(sels, form):
    if "target" not in sels:
        raise err_types.DoesNotExistError("Target does not exist.")
    sel = sels["target"]
    sel_types.check_selection(sel)

    # In multi-element selections, it is possible
    # for the start value(s) to be greater than the end value(s).
    # In single-element selections, the end value(s) is always
    # greater than the start value(s).
    sel_mode = sel_modes.from_selection(sel)
    if isinstance(sel, sel_types.RowRange):
        if sel.end.value - sel.start.value == 1:
            pass
            sel = sel_types.RowIndex(sel.start.value)
        else:
            raise err_types.NotSupportedError(
                f"Selection mode {sel_mode.value} "
                "is not supported with paste operation. "
                "Select a single row instead."
            )
    elif isinstance(sel, sel_types.ColRange):
        if sel.end.value - sel.start.value == 1:
            sel = sel_types.ColIndex(sel.start.value)
        else:
            raise err_types.NotSupportedError(
                f"Selection mode {sel_mode.value} "
                "is not supported with paste operation. "
                "Select a single column instead."
            )
    elif isinstance(sel, sel_types.Box):
        if sel.row_range.end.value - sel.row_range.start.value == 1 \
                and sel.col_range.end.value - sel.col_range.start.value == 1:
            sel = sel_types.CellPosition(
                row_index=sel_types.RowIndex(sel.row_range.start.value),
                col_index=sel_types.ColIndex(sel.col_range.start.value),
            )
        else:
            raise err_types.NotSupportedError(
                f"Selection mode {sel_mode.value} "
                "is not supported with paste operation. "
                "Select a single cell instead."
            )

    sel_mode = sel_modes.from_selection(sel)

    copy_to_paste = {
        sel_types.Mode.ROWS: sel_types.Mode.ROW_INDEX,
        sel_types.Mode.COLUMNS: sel_types.Mode.COLUMN_INDEX,
        sel_types.Mode.BOX: sel_types.Mode.CELL_POSITION,
    }
    copy_selection_mode = state.get_buffer_mode()

    selection_mode_options = []
    if copy_selection_mode is None:
        raise err_types.UserError("Cannot paste because nothing is copied to buffer yet.")
    elif copy_selection_mode not in copy_to_paste:
        raise err_types.NotSupportedError(
            f"Unexpected copy type {copy_selection_mode} "
            "is not supported by paste."
        )
    else:
        selection_mode_options = [copy_to_paste[copy_selection_mode]]

    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode.value} "
            "is not supported with paste operation for copied buffer."
        )

    modification = modifications.Modification(
        operation=modifications.Type.PASTE,
        input=sel,
    )
    return [modification]


def validate_and_parse_delete(sels, form):
    if "default" not in sels:
        raise err_types.DoesNotExistError("Selection does not exist.")
    sel = sels["default"]
    sel_types.check_selection(sel)

    sel_mode = sel_modes.from_selection(sel)
    selection_mode_options = [
        sel_types.Mode.ROWS,
        sel_types.Mode.COLUMNS,
    ]
    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode.value} "
            "is not supported with delete operation."
        )

    modification = modifications.Modification(
        operation=modifications.Type.DELETE,
        input=sel,
    )
    return [modification]


def validate_and_parse_move(sels, form):
    if "default" not in sels:
        raise err_types.DoesNotExistError("Selection does not exist.")
    sel = sels["default"]
    sel_types.check_selection(sel)
    if "target" not in sels:
        raise err_types.DoesNotExistError("Target does not exist.")
    target = sels["target"]
    sel_types.check_selection(target)

    sel_mode = sel_modes.from_selection(sel)
    target_mode = sel_modes.from_selection(target)
    num = None
    adjusted_target = None
    if isinstance(sel, sel_types.RowRange):
      if isinstance(target, sel_types.RowIndex):
        pass
      elif isinstance(target, sel_types.RowRange):
          if target.end.value - target.start.value == 1:
              target = sel_types.RowIndex(target.start.value)
          else:
              raise err_types.NotSupportedError(
                  f"Selection mode {target_mode} "
                  "is not supported as target for move operation. "
                  "Select a single row instead."
              )
      else:
        raise err_types.NotSupportedError(
            f"Selection mode {target_mode} "
            "is not supported as target for move operation."
        )
    
      num = sel.end.value - sel.start.value
      
      curr_pos = target.value
      if curr_pos < sel.start.value:
        adjusted_target = target
      elif curr_pos > sel.end.value:
        adjusted_target = sel_types.RowIndex(curr_pos - num)
      else:
        raise err_types.UserError(
          f"Cannot move selection to a target within original bounds."
        )
    elif isinstance(sel, sel_types.ColRange):
      if isinstance(target, sel_types.ColIndex):
        pass
      elif isinstance(target, sel_types.ColRange):
          if target.end.value - target.start.value == 1:
              target = sel_types.ColIndex(target.start.value)
          else:
              raise err_types.NotSupportedError(
                  f"Selection mode {target_mode} "
                  "is not supported as target for move operation. "
                  "Select a single column instead."
              )
      else:
        raise err_types.NotSupportedError(
            f"Selection mode {target_mode} "
            "is not supported as target for move operation."
        )

      num = sel.end.value - sel.start.value
      curr_pos = target.value
      if curr_pos < sel.start.value:
        adjusted_target = target
      elif curr_pos > sel.end.value:
        adjusted_target = sel_types.ColIndex(curr_pos - num)
      else:
        raise err_types.UserError(
          f"Cannot move selection to a target within original bounds."
        )
    else:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode.value} "
            "is not supported with move operation."
        )
    assert num is not None
    assert adjusted_target is not None

    mods = [
      modifications.Modification(
          operation=modifications.Type.COPY,
          input=sel,
      ),
      modifications.Modification(
          operation=modifications.Type.DELETE,
          input=sel,
      ),
      modifications.Modification(
          operation=modifications.Type.INSERT,
          input=modifications.InsertInput(
              selection=adjusted_target,
              number=num,
          )
      ),
      modifications.Modification(
          operation=modifications.Type.PASTE,
          input=adjusted_target,
      ),
    ]
    return mods


def validate_and_parse_insert(sels, form):
    if "target" not in sels:
        raise err_types.DoesNotExistError("Target does not exist.")
    sel = sels["target"]
    sel_types.check_selection(sel)

    # In multi-element selections, it is possible
    # for the start value(s) to be greater than the end value(s).
    # In single-element selections, the end value(s) is always
    # greater than the start value(s).
    sel_mode = sel_modes.from_selection(sel)
    if isinstance(sel, sel_types.RowRange):
        if sel.end.value - sel.start.value == 1:
            sel = sel_types.RowIndex(sel.start.value)
        else:
            raise err_types.NotSupportedError(
                f"Selection mode {sel_mode.value} "
                "is not supported with insert operation. "
                "Select a single row instead."
            )
    elif isinstance(sel, sel_types.ColRange):
        if sel.end.value - sel.start.value == 1:
            sel = sel_types.ColIndex(sel.start.value)
        else:
            raise err_types.NotSupportedError(
                f"Selection mode {sel_mode.value} "
                "is not supported with insert operation. "
                "Select a single column instead."
            )

    sel_mode = sel_modes.from_selection(sel)
    selection_mode_options = [
        sel_types.Mode.ROW_INDEX,
        sel_types.Mode.COLUMN_INDEX,
    ]
    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode.value} "
            "is not supported with insert operation."
        )

    number = form_helpers.extract(form, "insert-number", name="number")
    form_helpers.validate_nonempty(number, name="number")
    number = form_helpers.parse_int(number, name="number")

    inp = modifications.InsertInput(
        selection=sel,
        number=number,
    )
    modification = modifications.Modification(
        operation=modifications.Type.INSERT,
        input=inp,
    )
    return [modification]


def validate_and_parse_insert_end_rows(sels, form):
    number = form_helpers.extract(form, "insert-number", name="number")
    form_helpers.validate_nonempty(number, name="number")
    number = form_helpers.parse_int(number, name="number")

    bounds = sheet.data.get_bounds()
    sel = sel_types.RowIndex(bounds.row.value)

    inp = modifications.InsertInput(
        selection=sel,
        number=number,
    )
    modification = modifications.Modification(
        operation=modifications.Type.INSERT,
        input=inp,
    )
    return [modification]


def validate_and_parse_insert_end_cols(sels, form):
    number = form_helpers.extract(form, "insert-number", name="number")
    form_helpers.validate_nonempty(number, name="number")
    number = form_helpers.parse_int(number, name="number")

    bounds = sheet.data.get_bounds()
    sel = sel_types.ColIndex(bounds.col.value)

    inp = modifications.InsertInput(
        selection=sel,
        number=number,
    )
    modification = modifications.Modification(
        operation=modifications.Type.INSERT,
        input=inp,
    )
    return [modification]


def validate_and_parse_erase(sels, form):
    if "default" not in sels:
        raise err_types.DoesNotExistError("Selection does not exist.")
    sel = sels["default"]
    sel_types.check_selection(sel)

    sel_mode = sel_modes.from_selection(sel)
    selection_mode_options = [
        sel_types.Mode.ROWS,
        sel_types.Mode.COLUMNS,
        sel_types.Mode.BOX,
    ]
    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode.value} "
            "is not supported with erase operation."
        )

    inp = modifications.ValueInput(selection=sel, value=None)
    modification = modifications.Modification(
        operation=modifications.Type.VALUE,
        input=inp,
    )
    return [modification]


def validate_and_parse_value(sels, form):
    if "default" not in sels:
        raise err_types.DoesNotExistError("Selection does not exist.")
    sel = sels["default"]
    sel_types.check_selection(sel)

    sel_mode = sel_modes.from_selection(sel)
    selection_mode_options = [
        sel_types.Mode.ROWS,
        sel_types.Mode.COLUMNS,
        sel_types.Mode.BOX,
    ]
    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode.value} "
            "is not supported with value operation."
        )

    value = form_helpers.extract(form, "value", name="value")
    if value == "":
        raise err_types.InputError("Field 'value' was not given.")

    inp = modifications.ValueInput(selection=sel, value=value)
    modification = modifications.Modification(
        operation=modifications.Type.VALUE,
        input=inp,
    )
    return [modification]


def apply_cut(mods):
    assert len(mods) == 2
    copy_mod = mods[0]
    assert copy_mod.operation == modifications.Type.COPY
    sel = copy_mod.input

    state.set_buffer_mode(sel)
    for modification in mods:
        modifications.apply_modification(modification)


def apply_copy(mods):
    assert len(mods) == 1
    copy_mod = mods[0]
    assert copy_mod.operation == modifications.Type.COPY
    sel = copy_mod.input

    state.set_buffer_mode(sel)
    for modification in mods:
        modifications.apply_modification(modification)


def apply_paste(mods):
    for modification in mods:
        modifications.apply_modification(modification)


def apply_delete(mods):
    for modification in mods:
        modifications.apply_modification(modification)


def apply_move(mods):
    for modification in mods:
        modifications.apply_modification(modification)

    # update selection to wherever cells ended up
    copy_mod = mods[0]
    assert copy_mod.operation == modifications.Type.COPY
    sel = copy_mod.input
    
    paste_mod = mods[-1]
    assert paste_mod.operation == modifications.Type.PASTE
    target = paste_mod.input

    new_start = target.value
    if isinstance(sel, sel_types.RowRange): 
      num = sel.end.value - sel.start.value
      new_sel = sel_types.RowRange(
        start=sheet_types.Index(new_start),
        end=sheet_types.Bound(new_start + num),
      )
      sel_state.set_selection(new_sel)
    elif isinstance(sel, sel_types.ColRange): 
      num = sel.end.value - sel.start.value
      new_sel = sel_types.ColRange(
        start=sheet_types.Index(new_start),
        end=sheet_types.Bound(new_start + num),
      )
      sel_state.set_selection(new_sel)
    

def apply_insert(mods):
    for modification in mods:
        modifications.apply_modification(modification)


def apply_insert_end_rows(mods):
    for modification in mods:
        modifications.apply_modification(modification)


def apply_insert_end_cols(mods):
    for modification in mods:
        modifications.apply_modification(modification)


def apply_erase(mods):
    for modification in mods:
        modifications.apply_modification(modification)


def apply_value(mods):
    for modification in mods:
        modifications.apply_modification(modification)


def render_cut_inputs():
    use_sel = render_use_selection("cut", "default")
    return render_template(
            "partials/bulk_editor/cut.html",
            use_sel=use_sel,
    )


def render_copy_inputs():
    use_sel = render_use_selection("copy", "default")
    return render_template(
            "partials/bulk_editor/copy.html",
            use_sel=use_sel,
    )


def render_paste_inputs():
    use_sel = render_use_selection("paste", "target")
    return render_template(
            "partials/bulk_editor/paste.html",
            use_sel=use_sel,
    )


def render_delete_inputs():
    use_sel = render_use_selection("delete", "default")
    return render_template(
            "partials/bulk_editor/delete.html",
            use_sel=use_sel,
    )


def render_move_inputs():
    use_sel_default = render_use_selection("move", "default")
    use_sel_target = render_use_selection("move", "target")
    return render_template(
            "partials/bulk_editor/move.html",
            use_sel_default=use_sel_default,
            use_sel_target=use_sel_target,
    )


def render_insert_inputs():
    use_sel = render_use_selection("insert", "target")
    return render_template(
            "partials/bulk_editor/insert.html",
            use_sel=use_sel,
    )


def render_insert_end_rows_inputs():
    return render_template(
            "partials/bulk_editor/insert_end.html",
            use_sel="",
    )


def render_insert_end_cols_inputs():
    return render_template(
            "partials/bulk_editor/insert_end.html",
            use_sel="",
    )


def render_erase_inputs():
    use_sel = render_use_selection("erase", "default")
    return render_template(
            "partials/bulk_editor/erase.html",
            use_sel=use_sel,
    )


def render_value_inputs():
    show_help = command_palette.state.get_show_help()
    use_sel = render_use_selection("value", "default")
    return render_template(
            "partials/bulk_editor/value.html",
            show_help=show_help,
            use_sel=use_sel,
            value="",
    )


all_operations = {
    types.Name.CUT: types.Operation(
        name=types.Name.CUT,
        icon="✂",
        validate_and_parse=validate_and_parse_cut,
        apply=apply_cut,
        render=render_cut_inputs,
    ),
    types.Name.COPY: types.Operation(
        name=types.Name.COPY,
        icon="⧉",
        validate_and_parse=validate_and_parse_copy,
        apply=apply_copy,
        render=render_copy_inputs,
    ),
    types.Name.PASTE: types.Operation(
        name=types.Name.PASTE,
        icon="📋",
        validate_and_parse=validate_and_parse_paste,
        apply=apply_paste,
        render=render_paste_inputs,
    ),
    types.Name.DELETE: types.Operation(
        name=types.Name.DELETE,
        icon="❌",
        validate_and_parse=validate_and_parse_delete,
        apply=apply_delete,
        render=render_delete_inputs,
    ),
    types.Name.MOVE: types.Operation(
        name=types.Name.MOVE,
        icon="❖",
        validate_and_parse=validate_and_parse_move,
        apply=apply_move,
        render=render_move_inputs,
    ),
    types.Name.INSERT: types.Operation(
        name=types.Name.INSERT,
        icon="➕",
        validate_and_parse=validate_and_parse_insert,
        apply=apply_insert,
        render=render_insert_inputs,
    ),
    types.Name.ERASE: types.Operation(
        name=types.Name.ERASE,
        icon="🗑",
        validate_and_parse=validate_and_parse_erase,
        apply=apply_erase,
        render=render_erase_inputs,
    ),
    types.Name.VALUE: types.Operation(
        name=types.Name.VALUE,
        icon="½",
        validate_and_parse=validate_and_parse_value,
        apply=apply_value,
        render=render_value_inputs,
    ),
}


options = list(all_operations.keys())


def get(name):
    if name not in all_operations:
        raise err_types.UnknownOptionError(f"Unknown operation: {name.value}.")
    operation = all_operations[name]
    return operation


def get_all():
    return options


def get_modifications(name):
    bounds = sheet.data.get_bounds()
    sel = sel_state.get_selection()

    op = None
    mods = None
    match name:
        case types.Name.CUT:
            sels = {"default": sel}
            op = types.Name.CUT
            operation = get(op)
            mods = operation.validate_and_parse(sels, None)
        case types.Name.COPY:
            sels = {"default": sel}
            op = types.Name.COPY
            operation = get(op)
            mods = operation.validate_and_parse(sels, None)
        case types.Name.PASTE:
            sels = {"target": sel}
            op = types.Name.PASTE
            operation = get(op)
            mods = operation.validate_and_parse(sels, None)
        case types.Name.INSERT:
            sels = {"target": sel}
            op = types.Name.INSERT
            operation = get(op)
            mods = operation.validate_and_parse(sels, {"insert-number": "1"})
        case types.Name.DELETE:
            sels = {"default": sel}
            op = types.Name.DELETE
            operation = get(op)
            mods = operation.validate_and_parse(sels, None)
        case types.Name.MOVE_FORWARD:
            op = types.Name.MOVE
            operation = get(op)

            new_pos = sel.end.value + 1
            if isinstance(sel, sel_types.RowRange):
              if new_pos > bounds.row.value:
                raise err_types.UserError("Cannot move forward anymore.")
              target = sel_types.RowIndex(new_pos)
            elif isinstance(sel, sel_types.ColRange):
              if new_pos > bounds.col.value:
                raise err_types.UserError("Cannot move forward anymore.")
              target = sel_types.ColIndex(new_pos)
            else:
              sel_mode = sel_modes.from_selection(sel)
              raise err_types.NotSupportedError(
                  f"Selection mode {sel_mode.value} "
                  "is not supported with move operation."
              )
            sels = {"default": sel, "target": target}

            mods = operation.validate_and_parse(sels, None)
        case types.Name.MOVE_BACKWARD:
            op = types.Name.MOVE
            operation = get(op)

            new_pos = sel.start.value - 1
            if isinstance(sel, sel_types.RowRange):
              if new_pos < 0:
                raise err_types.UserError("Cannot move backward anymore.")
              target = sel_types.RowIndex(new_pos)
            elif isinstance(sel, sel_types.ColRange):
              if new_pos < 0:
                raise err_types.UserError("Cannot move backward anymore.")
              target = sel_types.ColIndex(new_pos)
            else:
              sel_mode = sel_modes.from_selection(sel)
              raise err_types.NotSupportedError(
                  f"Selection mode {sel_mode.value} "
                  "is not supported with move operation."
              )
            sels = {"default": sel, "target": target}

            mods = operation.validate_and_parse(sels, None)
        case types.Name.INSERT_END_ROWS:
            op = types.Name.INSERT
            operation = get(op)
            target = sel_types.RowIndex(bounds.row.value)
            sels = {"target": target}
            mods = operation.validate_and_parse(sels, {"insert-number": "1"})
        case types.Name.INSERT_END_COLS:
            op = types.Name.INSERT
            operation = get(op)
            target = sel_types.ColIndex(bounds.col.value)
            sels = {"target": target}
            mods = operation.validate_and_parse(sels, {"insert-number": "1"})
        case _:
            raise err_types.NotSupportedError(
                f"Cannot get modifications for operation {name.value} "
                "without additional inputs."
            )

    assert op is not None
    assert mods is not None

    return op, mods


def validate_and_parse(name, form):
    operation = get(name)
    sels_for_op = state.get_selections()
    mods = operation.validate_and_parse(sels_for_op, form)
    return mods


def apply(name, mods):
    operation = get(name)
    operation.apply(mods)


def render(name):
    operation = get(name)
    return operation.render()
