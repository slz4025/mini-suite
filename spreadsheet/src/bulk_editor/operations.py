from dataclasses import dataclass
from enum import Enum
from flask import render_template
from typing import Callable, List, Optional

import src.command_palette as command_palette
import src.errors.types as err_types
import src.utils.form as form_helpers
import src.selector.modes as sel_modes
import src.selector.state as sel_state
import src.selector.types as sel_types
import src.sheet as sheet

import src.bulk_editor.modifications as modifications


class Name(Enum):
    CUT = 'Cut'
    COPY = 'Copy'
    PASTE = 'Paste'
    DELETE = 'Delete'
    INSERT = 'Insert'
    INSERT_END_ROWS = 'Insert End Rows'
    INSERT_END_COLS = 'Insert End Columns'
    ERASE = 'Erase'
    VALUE = 'Value'


def from_input(name_str):
    match name_str:
        case "Cut":
            return Name.CUT
        case "Copy":
            return Name.COPY
        case "Paste":
            return Name.PASTE
        case "Delete":
            return Name.DELETE
        case "Insert":
            return Name.INSERT
        case "Insert End Rows":
            return Name.INSERT_END_ROWS
        case "Insert End Columns":
            return Name.INSERT_END_COLS
        case "Erase":
            return Name.ERASE
        case "Value":
            return Name.VALUE
        case _:
            raise err_types.UnknownOptionError(
                f"Unknown operation: {name_str}."
            )


@dataclass
class Operation:
    name: Name
    icon: str
    validate_and_parse: Callable[[object], List[modifications.Modification]]
    apply: Callable[[List[modifications.Modification]], None]
    render: Callable[[], str]


def validate_and_parse_cut(form):
    sel = sel_state.get_selection()
    if sel is None:
        raise err_types.DoesNotExistError("Selection does not exist.")

    sel_mode = sel_modes.from_selection(sel)
    selection_mode_options = [
        sel_types.Mode.ROWS,
        sel_types.Mode.COLUMNS,
        sel_types.Mode.BOX,
    ]
    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode} "
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


def validate_and_parse_copy(form):
    sel = sel_state.get_selection()
    if sel is None:
        raise err_types.DoesNotExistError("Selection does not exist.")

    sel_mode = sel_modes.from_selection(sel)
    selection_mode_options = [
        sel_types.Mode.ROWS,
        sel_types.Mode.COLUMNS,
        sel_types.Mode.BOX,
    ]
    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode} "
            "is not supported with copy operation."
        )

    modification = modifications.Modification(
        operation=modifications.Type.COPY,
        input=sel,
    )
    return [modification]


def validate_and_parse_paste(form):
    sel = sel_state.get_selection()
    if sel is None:
        raise err_types.DoesNotExistError("Selection does not exist.")

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
                f"Selection mode {sel_mode} "
                "is not supported with paste operation. "
                "Select a single row instead."
            )
    elif isinstance(sel, sel_types.ColRange):
        if sel.end.value - sel.start.value == 1:
            sel = sel_types.ColIndex(sel.start.value)
        else:
            raise err_types.NotSupportedError(
                f"Selection mode {sel_mode} "
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
                f"Selection mode {sel_mode} "
                "is not supported with paste operation. "
                "Select a single cell instead."
            )

    sel_mode = sel_modes.from_selection(sel)

    copy_to_paste = {
        sel_types.Mode.ROWS: sel_types.Mode.ROW_INDEX,
        sel_types.Mode.COLUMNS: sel_types.Mode.COLUMN_INDEX,
        sel_types.Mode.BOX: sel_types.Mode.CELL_POSITION,
    }
    copy_selection_mode = sel_state.get_buffer_mode()

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
            f"Selection mode {sel_mode} "
            "is not supported with paste operation for copied buffer."
        )

    modification = modifications.Modification(
        operation=modifications.Type.PASTE,
        input=sel,
    )
    return [modification]


def validate_and_parse_delete(form):
    sel = sel_state.get_selection()
    if sel is None:
        raise err_types.DoesNotExistError("Selection does not exist.")

    sel_mode = sel_modes.from_selection(sel)
    selection_mode_options = [
        sel_types.Mode.ROWS,
        sel_types.Mode.COLUMNS,
    ]
    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode} "
            "is not supported with delete operation."
        )

    modification = modifications.Modification(
        operation=modifications.Type.DELETE,
        input=sel,
    )
    return [modification]


def validate_and_parse_insert(form):
    sel = sel_state.get_selection()
    if sel is None:
        raise err_types.DoesNotExistError("Selection does not exist.")

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
                f"Selection mode {sel_mode} "
                "is not supported with insert operation. "
                "Select a single row instead."
            )
    elif isinstance(sel, sel_types.ColRange):
        if sel.end.value - sel.start.value == 1:
            sel = sel_types.ColIndex(sel.start.value)
        else:
            raise err_types.NotSupportedError(
                f"Selection mode {sel_mode} "
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
            f"Selection mode {sel_mode} "
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


def validate_and_parse_insert_end_rows(form):
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


def validate_and_parse_insert_end_cols(form):
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


def validate_and_parse_erase(form):
    sel = sel_state.get_selection()
    if sel is None:
        raise err_types.DoesNotExistError("Selection does not exist.")

    sel_mode = sel_modes.from_selection(sel)
    selection_mode_options = [
        sel_types.Mode.ROWS,
        sel_types.Mode.COLUMNS,
        sel_types.Mode.BOX,
    ]
    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode} "
            "is not supported with erase operation."
        )

    inp = modifications.ValueInput(selection=sel, value=None)
    modification = modifications.Modification(
        operation=modifications.Type.VALUE,
        input=inp,
    )
    return [modification]


def validate_and_parse_value(form):
    sel = sel_state.get_selection()
    if sel is None:
        raise err_types.DoesNotExistError("Selection does not exist.")

    sel_mode = sel_modes.from_selection(sel)
    selection_mode_options = [
        sel_types.Mode.ROWS,
        sel_types.Mode.COLUMNS,
        sel_types.Mode.BOX,
    ]
    if not sel_mode in selection_mode_options:
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode} "
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

    sel_state.set_buffer_mode(sel)
    for modification in mods:
        modifications.apply_modification(modification)


def apply_copy(mods):
    assert len(mods) == 1
    copy_mod = mods[0]
    assert copy_mod.operation == modifications.Type.COPY
    sel = copy_mod.input

    sel_state.set_buffer_mode(sel)
    for modification in mods:
        modifications.apply_modification(modification)


def apply_paste(mods):
    for modification in mods:
        modifications.apply_modification(modification)


def apply_delete(mods):
    for modification in mods:
        modifications.apply_modification(modification)


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
    return render_template(
            "partials/bulk_editor/cut.html",
    )


def render_copy_inputs():
    return render_template(
            "partials/bulk_editor/copy.html",
    )


def render_paste_inputs():
    return render_template(
            "partials/bulk_editor/paste.html",
    )


def render_delete_inputs():
    return render_template(
            "partials/bulk_editor/delete.html",
    )


def render_insert_inputs():
    return render_template(
            "partials/bulk_editor/insert.html",
    )


def render_insert_end_rows_inputs():
    return render_template(
            "partials/bulk_editor/insert.html",
    )


def render_insert_end_cols_inputs():
    return render_template(
            "partials/bulk_editor/insert.html",
    )


def render_erase_inputs():
    return render_template(
            "partials/bulk_editor/erase.html",
    )


def render_value_inputs():
    show_help = command_palette.state.get_show_help()
    return render_template(
            "partials/bulk_editor/value.html",
            show_help=show_help,
            value="",
    )


all_operations = {
    Name.CUT: Operation(
        name=Name.CUT,
        icon="✂",
        validate_and_parse=validate_and_parse_cut,
        apply=apply_cut,
        render=render_cut_inputs,
    ),
    Name.COPY: Operation(
        name=Name.COPY,
        icon="⧉",
        validate_and_parse=validate_and_parse_copy,
        apply=apply_copy,
        render=render_copy_inputs,
    ),
    Name.PASTE: Operation(
        name=Name.PASTE,
        icon="📋",
        validate_and_parse=validate_and_parse_paste,
        apply=apply_paste,
        render=render_paste_inputs,
    ),
    Name.DELETE: Operation(
        name=Name.DELETE,
        icon="❌",
        validate_and_parse=validate_and_parse_delete,
        apply=apply_delete,
        render=render_delete_inputs,
    ),
    Name.INSERT: Operation(
        name=Name.INSERT,
        icon="➕",
        validate_and_parse=validate_and_parse_insert,
        apply=apply_insert,
        render=render_insert_inputs,
    ),
    Name.INSERT_END_ROWS: Operation(
        name=Name.INSERT_END_ROWS,
        icon="➕",
        validate_and_parse=validate_and_parse_insert_end_rows,
        apply=apply_insert_end_rows,
        render=render_insert_end_rows_inputs,
    ),
    Name.INSERT_END_COLS: Operation(
        name=Name.INSERT_END_COLS,
        icon="➕",
        validate_and_parse=validate_and_parse_insert_end_cols,
        apply=apply_insert_end_cols,
        render=render_insert_end_cols_inputs,
    ),
    Name.ERASE: Operation(
        name=Name.ERASE,
        icon="🗑",
        validate_and_parse=validate_and_parse_erase,
        apply=apply_erase,
        render=render_erase_inputs,
    ),
    Name.VALUE: Operation(
        name=Name.VALUE,
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


def render_option(option):
    show_help = command_palette.state.get_show_help()

    if not show_help:
        return option.value
    else:
        match option:
            case Name.CUT:
                return "{} [Ctrl+X]".format(option.value)
            case Name.COPY:
                return "{} [Ctrl+C]".format(option.value)
            case Name.PASTE:
                return "{} [Ctrl+V]".format(option.value)
            case Name.INSERT:
                return "{} [Ctrl+I]".format(option.value)
            case Name.INSERT_END_ROWS:
                return "{} [Ctrl+L]".format(option.value)
            case Name.INSERT_END_COLS:
                return "{} [Ctrl+Shift+L]".format(option.value)
            case Name.DELETE:
                return "{} [Delete]".format(option.value)
            case _:
                return option.value


def get_modifications(name):
    modifications = None

    match name:
        case Name.CUT:
            operation = get(name)
            modifications = operation.validate_and_parse(None)
        case Name.COPY:
            operation = get(name)
            modifications = operation.validate_and_parse(None)
        case Name.PASTE:
            operation = get(name)
            modifications = operation.validate_and_parse(None)
        case Name.INSERT:
            operation = get(name)
            modifications = operation.validate_and_parse({"insert-number": "1"})
        case Name.INSERT_END_ROWS:
            operation = get(name)
            modifications = operation.validate_and_parse({"insert-number": "1"})
        case Name.INSERT_END_COLS:
            operation = get(name)
            modifications = operation.validate_and_parse({"insert-number": "1"})
        case Name.DELETE:
            operation = get(name)
            modifications = operation.validate_and_parse(None)
        case _:
            raise err_types.NotSupportedError(
                f"Cannot get modifications for operation {name.value} "
                "without additional inputs."
            )

    assert modifications is not None
    return modifications


def validate_and_parse(name, form):
    operation = get(name)
    modifications = operation.validate_and_parse(form)
    return modifications


def apply(name, modifications):
    operation = get(name)
    operation.apply(modifications)


def render(name_str):
    name = from_input(name_str)
    operation = get(name)
    return operation.render()
