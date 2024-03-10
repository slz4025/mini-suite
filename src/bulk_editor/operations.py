from dataclasses import dataclass
from flask import render_template
from typing import Callable, List

import src.errors as errors
import src.form_helpers as form_helpers
import src.selection.inputs as sel_inputs
import src.selection.state as sel_state
import src.selection.types as sel_types
import src.data.operations as operations


@dataclass
class OperationForm:
    name: str
    allow_with_selection: Callable[[object, str], bool]
    validate_and_parse: Callable[
        [object, object],
        List[operations.Modification],
    ]
    apply: Callable[[object, List[operations.Modification]], None]
    render: Callable[[object], str]


def allow_cut_with_selection(session, mode):
    selection_mode_options = [
        "Rows",
        "Columns",
        "Box",
    ]
    return mode in selection_mode_options


def allow_copy_with_selection(session, mode):
    selection_mode_options = [
        "Rows",
        "Columns",
        "Box",
    ]
    return mode in selection_mode_options


def allow_paste_with_selection(session, mode):
    copy_to_paste = {
        "Rows": "Row",
        "Columns": "Column",
        "Box": "Cell Position",
    }
    copy_selection_mode = sel_state.get_buffer_mode(session)

    selection_mode_options = []
    if copy_selection_mode is None:
        pass
    elif copy_selection_mode not in copy_to_paste:
        raise errors.UnknownOptionError(
            f"Unexpected copy type {copy_selection_mode} "
            "is not supported by paste."
        )
    else:
        selection_mode_options = [copy_to_paste[copy_selection_mode]]
    return mode in selection_mode_options


def allow_delete_with_selection(session, mode):
    selection_mode_options = [
        "Rows",
        "Columns",
    ]
    return mode in selection_mode_options


def allow_insert_with_selection(session, mode):
    selection_mode_options = [
        "Row",
        "Column",
    ]
    return mode in selection_mode_options


def allow_erase_with_selection(session, mode):
    selection_mode_options = [
        "Rows",
        "Columns",
        "Box",
    ]
    return mode in selection_mode_options


def allow_value_with_selection(session, mode):
    selection_mode_options = [
        "Rows",
        "Columns",
        "Box",
    ]
    return mode in selection_mode_options


def validate_and_parse_cut(session, form):
    sel = sel_state.get_selection(session)

    sel_mode = sel_inputs.mode_from_selection(sel)
    if not allow_cut_with_selection(session, sel_mode):
        raise errors.UnknownOptionError(
            f"Selection mode {sel_mode} "
            "is not supported with cut operation."
        )

    modifications = []

    modification = operations.Modification(operation="COPY", input=sel)
    modifications.append(modification)

    inp = operations.ValueInput(selection=sel, value=None)
    modification = operations.Modification(operation="VALUE", input=inp)
    modifications.append(modification)

    return modifications


def validate_and_parse_copy(session, form):
    sel = sel_state.get_selection(session)

    sel_mode = sel_inputs.mode_from_selection(sel)
    if not allow_copy_with_selection(session, sel_mode):
        raise errors.UnknownOptionError(
            f"Selection mode {sel_mode} "
            "is not supported with copy operation."
        )

    modification = operations.Modification(operation="COPY", input=sel)
    return [modification]


def validate_and_parse_paste(session, form):
    sel = sel_state.get_selection(session)

    # In multi-element selections, it is possible
    # for the start value(s) to be greater than the end value(s).
    # In single-element selections, the end value(s) is always
    # greater than the start value(s).
    sel_mode = sel_inputs.mode_from_selection(sel)
    if isinstance(sel, sel_types.RowRange):
        if sel.end.value - sel.start.value == 1:
            pass
            sel = sel_types.RowIndex(sel.start.value)
        else:
            raise errors.UnknownOptionError(
                f"Selection mode {sel_mode} "
                "is not supported with paste operation. "
                "Select a single row instead."
            )
    elif isinstance(sel, sel_types.ColRange):
        if sel.end.value - sel.start.value == 1:
            sel = sel_types.ColIndex(sel.start.value)
        else:
            raise errors.UnknownOptionError(
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
            raise errors.UnknownOptionError(
                f"Selection mode {sel_mode} "
                "is not supported with paste operation. "
                "Select a single cell instead."
            )

    sel_mode = sel_inputs.mode_from_selection(sel)
    if not allow_paste_with_selection(session, sel_mode):
        raise errors.UnknownOptionError(
            f"Selection mode {sel_mode} "
            "is not supported with paste operation."
        )

    modification = operations.Modification(operation="PASTE", input=sel)
    return [modification]


def validate_and_parse_delete(session, form):
    sel = sel_state.get_selection(session)

    sel_mode = sel_inputs.mode_from_selection(sel)
    if not allow_delete_with_selection(session, sel_mode):
        raise errors.UnknownOptionError(
            f"Selection mode {sel_mode} "
            "is not supported with delete operation."
        )

    modification = operations.Modification(operation="DELETE", input=sel)
    return [modification]


def validate_and_parse_insert(session, form):
    sel = sel_state.get_selection(session)

    sel_mode = sel_inputs.mode_from_selection(sel)
    if not allow_insert_with_selection(session, sel_mode):
        raise errors.UnknownOptionError(
            f"Selection mode {sel_mode} "
            "is not supported with insert operation."
        )

    number = form_helpers.extract(form, "insert-number", name="number")
    form_helpers.validate_nonempty(number, name="number")
    number = form_helpers.parse_int(number, name="number")

    inp = operations.InsertInput(
        selection=sel,
        number=number,
    )
    modification = operations.Modification(operation="INSERT", input=inp)
    return [modification]


def validate_and_parse_erase(session, form):
    sel = sel_state.get_selection(session)

    sel_mode = sel_inputs.mode_from_selection(sel)
    if not allow_erase_with_selection(session, sel_mode):
        raise errors.UnknownOptionError(
            f"Selection mode {sel_mode} "
            "is not supported with erase operation."
        )

    inp = operations.ValueInput(selection=sel, value=None)
    modification = operations.Modification(operation="VALUE", input=inp)
    return [modification]


def validate_and_parse_value(session, form):
    sel = sel_state.get_selection(session)

    sel_mode = sel_inputs.mode_from_selection(sel)
    if not allow_value_with_selection(session, sel_mode):
        raise errors.UnknownOptionError(
            f"Selection mode {sel_mode} "
            "is not supported with value operation."
        )

    value = form_helpers.extract(form, "value", name="value")
    if value == "":
        raise errors.UserError("Field 'value' was not given.")

    inp = operations.ValueInput(selection=sel, value=value)
    modification = operations.Modification(operation="Value", input=inp)
    return [modification]


def apply_cut(session, modifications):
    sel = sel_state.get_selection(session)
    sel_state.set_buffer_mode(session, sel)
    for modification in modifications:
        operations.apply_modification(modification)


def apply_copy(session, modifications):
    sel = sel_state.get_selection(session)
    sel_state.set_buffer_mode(session, sel)
    for modification in modifications:
        operations.apply_modification(modification)


def apply_paste(session, modifications):
    for modification in modifications:
        operations.apply_modification(modification)


def apply_delete(session, modifications):
    for modification in modifications:
        operations.apply_modification(modification)


def apply_insert(session, modifications):
    for modification in modifications:
        operations.apply_modification(modification)


def apply_erase(session, modifications):
    for modification in modifications:
        operations.apply_modification(modification)


def apply_value(session, modifications):
    for modification in modifications:
        operations.apply_modification(modification)


def render_copy_inputs(session):
    return render_template(
            "partials/bulk_editor/copy.html",
    )


def render_cut_inputs(session):
    return render_template(
            "partials/bulk_editor/cut.html",
    )


def render_paste_inputs(session):
    return render_template(
            "partials/bulk_editor/paste.html",
    )


def render_delete_inputs(session):
    return render_template(
            "partials/bulk_editor/delete.html",
    )


def render_insert_inputs(session):
    return render_template(
            "partials/bulk_editor/insert.html",
    )


def render_erase_inputs(session):
    return render_template(
            "partials/bulk_editor/erase.html",
    )


def render_value_inputs(session):
    return render_template(
            "partials/bulk_editor/value.html",
            value="",
    )


operation_forms = {
    "CUT": OperationForm(
        name="CUT",
        allow_with_selection=allow_cut_with_selection,
        validate_and_parse=validate_and_parse_cut,
        apply=apply_cut,
        render=render_cut_inputs,
    ),
    "COPY": OperationForm(
        name="COPY",
        allow_with_selection=allow_copy_with_selection,
        validate_and_parse=validate_and_parse_copy,
        apply=apply_copy,
        render=render_copy_inputs,
    ),
    "PASTE": OperationForm(
        name="PASTE",
        allow_with_selection=allow_paste_with_selection,
        validate_and_parse=validate_and_parse_paste,
        apply=apply_paste,
        render=render_paste_inputs,
    ),
    "DELETE": OperationForm(
        name="DELETE",
        allow_with_selection=allow_delete_with_selection,
        validate_and_parse=validate_and_parse_delete,
        apply=apply_delete,
        render=render_delete_inputs,
    ),
    "INSERT": OperationForm(
        name="INSERT",
        allow_with_selection=allow_insert_with_selection,
        validate_and_parse=validate_and_parse_insert,
        apply=apply_insert,
        render=render_insert_inputs,
    ),
    "ERASE": OperationForm(
        name="ERASE",
        allow_with_selection=allow_erase_with_selection,
        validate_and_parse=validate_and_parse_erase,
        apply=apply_erase,
        render=render_erase_inputs,
    ),
    "VALUE": OperationForm(
        name="VALUE",
        allow_with_selection=allow_value_with_selection,
        validate_and_parse=validate_and_parse_value,
        apply=apply_value,
        render=render_value_inputs,
    ),
}


options = list(operation_forms.keys())


def get(name):
    if name not in operation_forms:
        raise errors.UnknownOptionError(f"Unknown operation type: {name}.")
    operation_form = operation_forms[name]
    return operation_form


def get_allowed_options(session):
    allowed_options = []

    selection_mode = sel_state.get_mode(session)
    if selection_mode is not None:
        for o in options:
            operation_form = get(o)
            if operation_form.allow_with_selection(session, selection_mode):
                allowed_options.append(o)

    return allowed_options


def get_modifications(session, op):
    modifications = None

    match op:
        case "CUT":
            operation_form = get(op)
            modifications = operation_form.validate_and_parse(session, None)
        case "COPY":
            operation_form = get(op)
            modifications = operation_form.validate_and_parse(session, None)
        case "PASTE":
            operation_form = get(op)
            modifications = operation_form.validate_and_parse(session, None)
        case "DELETE":
            operation_form = get(op)
            modifications = operation_form.validate_and_parse(session, None)
        case _:
            raise errors.UnknownOptionError(
                "Cannot get modifications for operation {op} "
                "without additional inputs."
            )

    assert modifications is not None
    return modifications


def validate_and_parse(session, form):
    op = form_helpers.extract(form, "operation")
    operation_form = get(op)
    modifications = operation_form.validate_and_parse(session, form)
    return op, modifications


def apply(session, op, modifications):
    operation_form = get(op)
    operation_form.apply(session, modifications)


def render(session, operation):
    operation_form = get(operation)
    return operation_form.render(session)
