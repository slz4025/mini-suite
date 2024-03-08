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
    validate_and_parse: Callable[[object, object], operations.Input]
    render: Callable[[object], str]


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


def retrieve_selection(session, form):
    sel = sel_state.get_selection(session)
    return sel


def validate_and_parse_insert(session, form):
    sel = sel_state.get_selection(session)

    number = form_helpers.extract(form, "insert-number", name="number")
    form_helpers.validate_nonempty(number, name="number")
    number = form_helpers.parse_int(number, name="number")

    return operations.InsertInput(
        selection=sel,
        number=number,
    )


def validate_and_parse_value(session, form):
    sel = sel_state.get_selection(session)

    value = form_helpers.extract(form, "value", name="value")
    if value == "":
        raise errors.UserError("Field 'value' was not given.")

    return operations.ValueInput(selection=sel, value=value)


def render_copy_inputs(session):
    return render_template(
            "partials/bulk_editor/copy.html",
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
    "COPY": OperationForm(
        name="COPY",
        allow_selection=allow_copy_selection,
        validate_and_parse=retrieve_selection,
        render=render_copy_inputs,
    ),
    "PASTE": OperationForm(
        name="PASTE",
        allow_selection=allow_paste_selection,
        validate_and_parse=retrieve_selection,
        render=render_paste_inputs,
    ),
    "DELETE": OperationForm(
        name="DELETE",
        allow_selection=allow_delete_selection,
        validate_and_parse=retrieve_selection,
        render=render_delete_inputs,
    ),
    "INSERT": OperationForm(
        name="INSERT",
        allow_selection=allow_insert_selection,
        validate_and_parse=validate_and_parse_insert,
        render=render_insert_inputs,
    ),
    "ERASE": OperationForm(
        name="ERASE",
        allow_selection=allow_erase_selection,
        validate_and_parse=retrieve_selection,
        render=render_erase_inputs,
    ),
    "VALUE": OperationForm(
        name="VALUE",
        allow_selection=allow_value_selection,
        validate_and_parse=validate_and_parse_value,
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


def validate_and_parse(session, form):
    op = form_helpers.extract(form, "operation")
    operation_form = get(op)
    input = operation_form.validate_and_parse(session, form)

    if operation_form.name == "COPY":
        selection = input
        sel_state.set_buffer_mode(session, selection)

    modification = operations.Modification(operation=op, input=input)
    return modification


def render(session, operation):
    operation_form = get(operation)
    return operation_form.render(session)
