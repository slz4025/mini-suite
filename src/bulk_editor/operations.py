from dataclasses import dataclass
from flask import render_template
from typing import Callable

import src.errors as errors
import src.form_helpers as form_helpers
import src.selection.state as sel_state
import src.data.operations as operations


@dataclass
class OperationForm:
    name: str
    allow_selection: Callable[[object, str], bool]
    apply: Callable[[object, object], None]
    render: Callable[[object], str]


def allow_cut_selection(session, mode):
    selection_mode_options = [
        "Rows",
        "Columns",
        "Box",
    ]
    return mode in selection_mode_options


def allow_copy_selection(session, mode):
    selection_mode_options = [
        "Rows",
        "Columns",
        "Box",
    ]
    return mode in selection_mode_options


def allow_paste_selection(session, mode):
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


def allow_delete_selection(session, mode):
    selection_mode_options = [
        "Rows",
        "Columns",
    ]
    return mode in selection_mode_options


def allow_insert_selection(session, mode):
    selection_mode_options = [
        "Row",
        "Column",
    ]
    return mode in selection_mode_options


def allow_erase_selection(session, mode):
    selection_mode_options = [
        "Rows",
        "Columns",
        "Box",
    ]
    return mode in selection_mode_options


def allow_value_selection(session, mode):
    selection_mode_options = [
        "Rows",
        "Columns",
        "Box",
    ]
    return mode in selection_mode_options


def apply_cut(session, form):
    sel = sel_state.get_selection(session)
    sel_state.set_buffer_mode(session, sel)

    modification = operations.Modification(operation="COPY", input=sel)
    operations.apply_modification(modification)

    inp = operations.ValueInput(selection=sel, value=None)
    modification = operations.Modification(operation="VALUE", input=inp)
    operations.apply_modification(modification)


def apply_copy(session, form):
    sel = sel_state.get_selection(session)
    sel_state.set_buffer_mode(session, sel)

    modification = operations.Modification(operation="COPY", input=sel)
    operations.apply_modification(modification)


def apply_paste(session, form):
    sel = sel_state.get_selection(session)
    modification = operations.Modification(operation="PASTE", input=sel)
    operations.apply_modification(modification)


def apply_delete(session, form):
    sel = sel_state.get_selection(session)
    modification = operations.Modification(operation="DELETE", input=sel)
    operations.apply_modification(modification)


def apply_insert(session, form):
    sel = sel_state.get_selection(session)

    number = form_helpers.extract(form, "insert-number", name="number")
    form_helpers.validate_nonempty(number, name="number")
    number = form_helpers.parse_int(number, name="number")

    inp = operations.InsertInput(
        selection=sel,
        number=number,
    )
    modification = operations.Modification(operation="INSERT", input=inp)
    operations.apply_modification(modification)


def apply_erase(session, form):
    sel = sel_state.get_selection(session)
    inp = operations.ValueInput(selection=sel, value=None)
    modification = operations.Modification(operation="VALUE", input=inp)
    operations.apply_modification(modification)


def apply_value(session, form):
    sel = sel_state.get_selection(session)

    value = form_helpers.extract(form, "value", name="value")
    if value == "":
        raise errors.UserError("Field 'value' was not given.")

    inp = operations.ValueInput(selection=sel, value=value)
    modification = operations.Modification(operation="Value", input=inp)
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
        allow_selection=allow_cut_selection,
        apply=apply_cut,
        render=render_cut_inputs,
    ),
    "COPY": OperationForm(
        name="COPY",
        allow_selection=allow_copy_selection,
        apply=apply_copy,
        render=render_copy_inputs,
    ),
    "PASTE": OperationForm(
        name="PASTE",
        allow_selection=allow_paste_selection,
        apply=apply_paste,
        render=render_paste_inputs,
    ),
    "DELETE": OperationForm(
        name="DELETE",
        allow_selection=allow_delete_selection,
        apply=apply_delete,
        render=render_delete_inputs,
    ),
    "INSERT": OperationForm(
        name="INSERT",
        allow_selection=allow_insert_selection,
        apply=apply_insert,
        render=render_insert_inputs,
    ),
    "ERASE": OperationForm(
        name="ERASE",
        allow_selection=allow_erase_selection,
        apply=apply_erase,
        render=render_erase_inputs,
    ),
    "VALUE": OperationForm(
        name="VALUE",
        allow_selection=allow_value_selection,
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
            if operation_form.allow_selection(session, selection_mode):
                allowed_options.append(o)

    return allowed_options


def apply(session, form):
    op = form_helpers.extract(form, "operation")
    operation_form = get(op)
    operation_form.apply(session, form)


def render(session, operation):
    operation_form = get(operation)
    return operation_form.render(session)
