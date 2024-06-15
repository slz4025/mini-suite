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
    curr_name = state.get_current_operation()
    op = get(curr_name)
    sel = op.validate_selection(use, sel)
    state.set_selection(use, sel)


def get_selection(op_name, use):
    sels = state.get_selections()
    if use not in sels:
        raise err_types.DoesNotExistError(f"{op_name} operation has no {use} selection.")
    sel = sels[use]
    if sel is None:
        raise err_types.DoesNotExistError("{op_name} operation has no {use} selection.")
    return sel


def render_use_selection(op_name, use):
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
            op=op_name,
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
                f"Unknown bulk-editor operation: {name_str}."
            )


def validate_cut_selection(use, sel):
    sel_types.check_selection(sel)

    if use == "input":
        sel_mode = sel_modes.from_selection(sel)
        selection_mode_options = [
            sel_types.Mode.ROWS,
            sel_types.Mode.COLUMNS,
            sel_types.Mode.BOX,
        ]
        if sel_mode not in selection_mode_options:
            raise err_types.NotSupportedError(
                f"Cut operation does not support selection mode {sel_mode.value}."
            )
    else:
        raise err_types.NotSupportedError(f"Cut does not accept a selection of purpose {use}.")

    return sel


def validate_copy_selection(use, sel):
    sel_types.check_selection(sel)

    if use == "input":
        sel_mode = sel_modes.from_selection(sel)
        selection_mode_options = [
            sel_types.Mode.ROWS,
            sel_types.Mode.COLUMNS,
            sel_types.Mode.BOX,
        ]
        if sel_mode not in selection_mode_options:
            raise err_types.NotSupportedError(
                f"Copy operation does not support selection mode {sel_mode.value}."
            )
    else:
        raise err_types.NotSupportedError(f"Copy does not accept a selection of purpose {use}.")

    return sel


def validate_paste_selection(use, sel):
    sel_types.check_selection(sel)

    if use == "target":
        copy_to_paste = {
            sel_types.Mode.ROWS: sel_types.Mode.ROW_INDEX,
            sel_types.Mode.COLUMNS: sel_types.Mode.COLUMN_INDEX,
            sel_types.Mode.BOX: sel_types.Mode.CELL_POSITION,
        }
        copy_selection_mode = state.get_buffer_mode()

        selection_mode_options = []
        if copy_selection_mode is None:
            raise err_types.UserError("Paste operation has nothing to copy.")
        elif copy_selection_mode not in copy_to_paste:
            raise err_types.NotSupportedError(
                f"Paste operation does not support buffer selection type {copy_selection_mode.value}."
            )
        else:
            selection_mode_options = [copy_to_paste[copy_selection_mode]]

        # In multi-element selections, it is possible
        # for the start value(s) to be greater than the end value(s).
        # In single-element selections, the end value(s) is always
        # greater than the start value(s).
        target_mode = sel_modes.from_selection(sel)
        if isinstance(sel, sel_types.RowRange):
            if sel.end.value - sel.start.value == 1:
                sel = sel_types.RowIndex(sel.start.value)
            else:
                raise err_types.NotSupportedError(
                    f"Paste operation does not support target selection mode {target_mode.value}. "
                    "Select a single row instead."
                )
        elif isinstance(sel, sel_types.ColRange):
            if sel.end.value - sel.start.value == 1:
                sel = sel_types.ColIndex(sel.start.value)
            else:
                raise err_types.NotSupportedError(
                    f"Paste operation does not support target selection mode {target_mode.value}. "
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
                    f"Paste operation does not support target selection mode {target_mode.value}. "
                    "Select a single cell instead."
                )
        else:
            raise err_types.NotSupportedError(
                f"Paste operation does not support target selection mode {target_mode.value}."
            )

        target_mode = sel_modes.from_selection(sel)
        if target_mode not in selection_mode_options:
            raise err_types.NotSupportedError(
                f"Paste operation does not support target selection mode {target_mode.value} "
                f"for copied buffer type {copy_selection_mode.value}."
            )
    else:
        raise err_types.NotSupportedError(f"Paste does not accept a selection of purpose {use}.")

    return sel


def validate_delete_selection(use, sel):
    sel_types.check_selection(sel)

    if use == "input":
        sel_mode = sel_modes.from_selection(sel)
        selection_mode_options = [
            sel_types.Mode.ROWS,
            sel_types.Mode.COLUMNS,
        ]
        if sel_mode not in selection_mode_options:
            raise err_types.NotSupportedError(
                f"Delete operation does not support selection mode {sel_mode.value}."
            )
    else:
        raise err_types.NotSupportedError(f"Delete does not accept a selection of purpose {use}.")

    return sel

def validate_move_selection(use, sel):
    sel_types.check_selection(sel)

    if use == "input":
        sel_mode = sel_modes.from_selection(sel)
        if isinstance(sel, sel_types.RowRange):
            pass
        elif isinstance(sel, sel_types.ColRange):
            pass
        else:
            raise err_types.NotSupportedError(
                f"Move operation does not support input selection mode {sel_mode.value}."
            )
    elif use == "target":
        # requires input selection to be inputted first
        input_sel = get_selection("move", "input")
        sel_mode = sel_modes.from_selection(input_sel)

        target_mode = sel_modes.from_selection(sel)
        if isinstance(input_sel, sel_types.RowRange):
            if isinstance(sel, sel_types.RowIndex):
                pass
            elif isinstance(sel, sel_types.RowRange):
                if sel.end.value - sel.start.value == 1:
                    sel = sel_types.RowIndex(sel.start.value)
                else:
                    raise err_types.NotSupportedError(
                        f"Move operation does not support target selection mode {target_mode.value}. "
                        "Select a single row instead."
                    )
            else:
                raise err_types.NotSupportedError(
                    f"Move operation does not support target selection mode {target_mode.value} for input selection mode {sel_mode.value}."
                )
        elif isinstance(input_sel, sel_types.ColRange):
            if isinstance(sel, sel_types.ColIndex):
                pass
            elif isinstance(sel, sel_types.ColRange):
                if sel.end.value - sel.start.value == 1:
                    sel = sel_types.ColIndex(sel.start.value)
                else:
                    raise err_types.NotSupportedError(
                        f"Move operation does not support target selection mode {target_mode.value}. "
                        "Select a single column instead."
                    )
            else:
                raise err_types.NotSupportedError(
                    f"Move operation does not support target selection mode {target_mode.value} for input selection mode {sel_mode.value}."
                )
    else:
        raise err_types.NotSupportedError(f"Move does not accept a selection of purpose {use}.")

    return sel


def validate_insert_selection(use, sel):
    sel_types.check_selection(sel)

    if use == "target":
        # In multi-element selections, it is possible
        # for the start value(s) to be greater than the end value(s).
        # In single-element selections, the end value(s) is always
        # greater than the start value(s).
        target_mode = sel_modes.from_selection(sel)
        if isinstance(sel, sel_types.RowRange):
            if sel.end.value - sel.start.value == 1:
                sel = sel_types.RowIndex(sel.start.value)
            else:
                raise err_types.NotSupportedError(
                    f"Insert operation does not support target selection mode {target_mode.value}. "
                    "Select a single row instead."
                )
        elif isinstance(sel, sel_types.ColRange):
            if sel.end.value - sel.start.value == 1:
                sel = sel_types.ColIndex(sel.start.value)
            else:
                raise err_types.NotSupportedError(
                    f"Insert operation does not support target selection mode {target_mode.value}. "
                    "Select a single column instead."
                )

        selection_mode_options = [
            sel_types.Mode.ROW_INDEX,
            sel_types.Mode.COLUMN_INDEX,
        ]

        target_mode = sel_modes.from_selection(sel)
        if target_mode not in selection_mode_options:
            raise err_types.NotSupportedError(
                f"Insert operation does not support target selection mode {target_mode.value}."
            )
    else:
        raise err_types.NotSupportedError(f"Insert does not accept a selection of purpose {use}.")

    return sel


def validate_erase_selection(use, sel):
    sel_types.check_selection(sel)

    if use == "input":
        sel_mode = sel_modes.from_selection(sel)
        selection_mode_options = [
            sel_types.Mode.ROWS,
            sel_types.Mode.COLUMNS,
            sel_types.Mode.BOX,
        ]
        if sel_mode not in selection_mode_options:
            raise err_types.NotSupportedError(
                f"Erase operation does not support selection mode {sel_mode.value}."
            )
    else:
        raise err_types.NotSupportedError(f"Erase does not accept a selection of purpose {use}.")

    return sel


def validate_value_selection(use, sel):
    sel_types.check_selection(sel)

    if use == "input":
        sel_mode = sel_modes.from_selection(sel)
        selection_mode_options = [
            sel_types.Mode.ROWS,
            sel_types.Mode.COLUMNS,
            sel_types.Mode.BOX,
        ]
        if sel_mode not in selection_mode_options:
            raise err_types.NotSupportedError(
                f"Value operation does not support selection mode {sel_mode.value}."
            )
    else:
        raise err_types.NotSupportedError(f"Value does not accept a selection of purpose {use}.")

    return sel


def validate_and_parse_cut(form):
    sel = get_selection("cut", "input")

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


def validate_and_parse_copy(form):
    sel = get_selection("copy", "input")

    modification = modifications.Modification(
        operation=modifications.Type.COPY,
        input=sel,
    )
    return [modification]


def validate_and_parse_paste(form):
    target = get_selection("paste", "target")

    modification = modifications.Modification(
        operation=modifications.Type.PASTE,
        input=target,
    )
    return [modification]


def validate_and_parse_delete(form):
    sel = get_selection("delete", "input")

    modification = modifications.Modification(
        operation=modifications.Type.DELETE,
        input=sel,
    )
    return [modification]


def validate_and_parse_move(form):
    sel = get_selection("move", "input")
    target = get_selection("move", "target")

    num = None
    adjusted_target = None
    if isinstance(sel, sel_types.RowRange):
        assert isinstance(target, sel_types.RowIndex)

        num = sel.end.value - sel.start.value
        curr_pos = target.value
        if curr_pos < sel.start.value:
            adjusted_target = target
        elif curr_pos > sel.end.value:
            adjusted_target = sel_types.RowIndex(curr_pos - num)
        else:
            raise err_types.UserError(
                "Cannot move input selection to a target selection within original bounds."
            )
    elif isinstance(sel, sel_types.ColRange):
        assert isinstance(target, sel_types.ColIndex)

        num = sel.end.value - sel.start.value
        curr_pos = target.value
        if curr_pos < sel.start.value:
            adjusted_target = target
        elif curr_pos > sel.end.value:
            adjusted_target = sel_types.ColIndex(curr_pos - num)
        else:
            raise err_types.UserError(
                "Cannot move input selection to a target selection within original bounds."
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


def validate_and_parse_insert(form):
    target = get_selection("insert", "target")

    number = form_helpers.extract(form, "insert-number", name="number")
    form_helpers.validate_nonempty(number, name="number")
    number = form_helpers.parse_int(number, name="number")

    inp = modifications.InsertInput(
        selection=target,
        number=number,
    )
    modification = modifications.Modification(
        operation=modifications.Type.INSERT,
        input=inp,
    )
    return [modification]


def validate_and_parse_erase(form):
    sel = get_selection("erase", "input")

    inp = modifications.ValueInput(selection=sel, value=None)
    modification = modifications.Modification(
        operation=modifications.Type.VALUE,
        input=inp,
    )
    return [modification]


def validate_and_parse_value(form):
    sel = get_selection("value", "input")

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


def apply_erase(mods):
    for modification in mods:
        modifications.apply_modification(modification)


def apply_value(mods):
    for modification in mods:
        modifications.apply_modification(modification)


def render_cut_inputs():
    use_sel = render_use_selection("cut", "input")
    return render_template(
            "partials/bulk_editor/cut.html",
            use_sel=use_sel,
    )


def render_copy_inputs():
    use_sel = render_use_selection("copy", "input")
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
    use_sel = render_use_selection("delete", "input")
    return render_template(
            "partials/bulk_editor/delete.html",
            use_sel=use_sel,
    )


def render_move_inputs():
    use_sel_input = render_use_selection("move", "input")
    use_sel_target = render_use_selection("move", "target")
    return render_template(
            "partials/bulk_editor/move.html",
            use_sel_input=use_sel_input,
            use_sel_target=use_sel_target,
    )


def render_insert_inputs():
    use_sel = render_use_selection("insert", "target")
    return render_template(
            "partials/bulk_editor/insert.html",
            use_sel=use_sel,
    )


def render_erase_inputs():
    use_sel = render_use_selection("erase", "input")
    return render_template(
            "partials/bulk_editor/erase.html",
            use_sel=use_sel,
    )


def render_value_inputs():
    show_help = command_palette.state.get_show_help()
    use_sel = render_use_selection("value", "input")
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
        validate_selection=validate_cut_selection,
        validate_and_parse=validate_and_parse_cut,
        apply=apply_cut,
        render=render_cut_inputs,
    ),
    types.Name.COPY: types.Operation(
        name=types.Name.COPY,
        icon="⧉",
        validate_selection=validate_copy_selection,
        validate_and_parse=validate_and_parse_copy,
        apply=apply_copy,
        render=render_copy_inputs,
    ),
    types.Name.PASTE: types.Operation(
        name=types.Name.PASTE,
        icon="📋",
        validate_selection=validate_paste_selection,
        validate_and_parse=validate_and_parse_paste,
        apply=apply_paste,
        render=render_paste_inputs,
    ),
    types.Name.DELETE: types.Operation(
        name=types.Name.DELETE,
        icon="❌",
        validate_selection=validate_delete_selection,
        validate_and_parse=validate_and_parse_delete,
        apply=apply_delete,
        render=render_delete_inputs,
    ),
    types.Name.MOVE: types.Operation(
        name=types.Name.MOVE,
        icon="❖",
        validate_selection=validate_move_selection,
        validate_and_parse=validate_and_parse_move,
        apply=apply_move,
        render=render_move_inputs,
    ),
    types.Name.INSERT: types.Operation(
        name=types.Name.INSERT,
        icon="➕",
        validate_selection=validate_insert_selection,
        validate_and_parse=validate_and_parse_insert,
        apply=apply_insert,
        render=render_insert_inputs,
    ),
    types.Name.ERASE: types.Operation(
        name=types.Name.ERASE,
        icon="🗑",
        validate_selection=validate_erase_selection,
        validate_and_parse=validate_and_parse_erase,
        apply=apply_erase,
        render=render_erase_inputs,
    ),
    types.Name.VALUE: types.Operation(
        name=types.Name.VALUE,
        icon="½",
        validate_selection=validate_value_selection,
        validate_and_parse=validate_and_parse_value,
        apply=apply_value,
        render=render_value_inputs,
    ),
}


options = list(all_operations.keys())


def get(name):
    if name not in all_operations:
        raise err_types.UnknownOptionError(f"Unknown bulk-editor operation: {name.value}.")
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
            state.set_selection("input", sel)
            op = types.Name.CUT
            operation = get(op)
            mods = operation.validate_and_parse(None)
        case types.Name.COPY:
            state.set_selection("input", sel)
            op = types.Name.COPY
            operation = get(op)
            mods = operation.validate_and_parse(None)
        case types.Name.PASTE:
            state.set_selection("target", sel)
            op = types.Name.PASTE
            operation = get(op)
            mods = operation.validate_and_parse(None)
        case types.Name.INSERT:
            state.set_selection("target", sel)
            op = types.Name.INSERT
            operation = get(op)
            mods = operation.validate_and_parse({"insert-number": "1"})
        case types.Name.DELETE:
            state.set_selection("input", sel)
            op = types.Name.DELETE
            operation = get(op)
            mods = operation.validate_and_parse(None)
        case types.Name.MOVE_FORWARD:
            op = types.Name.MOVE
            operation = get(op)

            target = None
            if sel is not None:
                if isinstance(sel, sel_types.RowRange):
                    new_pos = sel.end.value + 1
                    if new_pos > bounds.row.value:
                        raise err_types.UserError("Cannot move rows forward anymore.")
                    target = sel_types.RowIndex(new_pos)
                elif isinstance(sel, sel_types.ColRange):
                    new_pos = sel.end.value + 1
                    if new_pos > bounds.col.value:
                        raise err_types.UserError("Cannot move columns forward anymore.")
                    target = sel_types.ColIndex(new_pos)
            state.set_selection("input", sel)
            state.set_selection("target", target)

            mods = operation.validate_and_parse(None)
        case types.Name.MOVE_BACKWARD:
            op = types.Name.MOVE
            operation = get(op)

            target = None
            if sel is not None:
                if isinstance(sel, sel_types.RowRange):
                    new_pos = sel.start.value - 1
                    if new_pos < 0:
                        raise err_types.UserError("Cannot move rows backward anymore.")
                    target = sel_types.RowIndex(new_pos)
                elif isinstance(sel, sel_types.ColRange):
                    new_pos = sel.start.value - 1
                    if new_pos < 0:
                        raise err_types.UserError("Cannot move columns backward anymore.")
                    target = sel_types.ColIndex(new_pos)
            state.set_selection("input", sel)
            state.set_selection("target", target)

            mods = operation.validate_and_parse(None)
        case types.Name.INSERT_END_ROWS:
            op = types.Name.INSERT
            operation = get(op)
            target = sel_types.RowIndex(bounds.row.value)
            state.set_selection("target", target)
            mods = operation.validate_and_parse({"insert-number": "1"})
        case types.Name.INSERT_END_COLS:
            op = types.Name.INSERT
            operation = get(op)
            target = sel_types.ColIndex(bounds.col.value)
            state.set_selection("target", target)
            mods = operation.validate_and_parse({"insert-number": "1"})
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
    mods = operation.validate_and_parse(form)
    return mods


def apply(name, mods):
    operation = get(name)
    operation.apply(mods)


def render(name):
    operation = get(name)
    return operation.render()
