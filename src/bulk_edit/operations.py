from dataclasses import dataclass
from flask import render_template
from typing import Callable

import src.errors as errors
import src.form_helpers as form_helpers

import src.bulk_edit.selection as selection
import src.bulk_edit.state as state

import src.data.operations as operations
import src.data.selections as selections


@dataclass
class OperationForm:
    name: str
    validate_and_parse: Callable[[object], operations.Input]
    render: Callable[[], str]


def validate_and_parse_insert(form):
    sel = selection.validate_and_parse(form)

    number = form_helpers.extract(form, "insert-number", name="number")
    form_helpers.validate_nonempty(number, name="number")
    number = form_helpers.parse_int(number, name="number")

    return operations.InsertInput(
        selection=sel,
        number=number,
    )


def validate_and_parse_value(form):
    sel = selection.validate_and_parse(form)

    value = form_helpers.extract(form, "value", name="value")
    if value == "":
        raise errors.UserError("Field 'value' was not given.")

    return operations.ValueInput(selection=sel, value=value)


def render_delete_inputs(session):
    selection_mode_options = [
        "Row",
        "Column",
        "Rows",
        "Columns",
    ]
    selection_form = selection.render(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/delete.html",
            selection_form=selection_form,
    )


def render_insert_inputs(session):
    selection_mode_options = [
        "Row",
        "Column",
    ]
    selection_form = selection.render(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/insert.html",
            selection_form=selection_form,
    )


def render_erase_inputs(session):
    selection_mode_options = [
        "Row",
        "Column",
        "Cell Position",
        "Rows",
        "Columns",
        "Box",
    ]
    selection_form = selection.render(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/erase.html",
            selection_form=selection_form,
    )


def render_value_inputs(session):
    selection_mode_options = [
        "Row",
        "Column",
        "Cell Position",
        "Rows",
        "Columns",
        "Box",
    ]
    selection_form = selection.render(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/value.html",
            value="",
            selection_form=selection_form,
    )


def save_copy_selection_mode(session, operation_input):
    input_type = type(operation_input)

    selection_mode = None
    if isinstance(operation_input, selections.RowIndex):
        selection_mode = "Row"
    elif isinstance(operation_input, selections.ColIndex):
        selection_mode = "Column"
    elif isinstance(operation_input, selections.CellPosition):
        selection_mode = "Cell Position"
    elif isinstance(operation_input, selections.RowRange):
        selection_mode = "Rows"
    elif isinstance(operation_input, selections.ColRange):
        selection_mode = "Columns"
    elif isinstance(operation_input, selections.Box):
        selection_mode = "Box"
    else:
        raise errors.UnknownOptionError(
            f"Unexpected type {input_type} is not valid copy input."
        )

    assert selection_mode is not None
    state.set_buffer_selection_mode(session, selection_mode)


def get_paste_selection_mode_options(session):
    copy_to_paste = {
        "Row": "Row",
        "Column": "Column",
        "Cell Position": "Cell Position",
        "Rows": "Row",
        "Columns": "Column",
        "Box": "Cell Position",
    }
    copy_selection_mode = state.get_buffer_selection_mode(session)
    if copy_selection_mode is None:
        raise errors.UserError("Did not copy anything yet to paste.")
    if copy_selection_mode not in copy_to_paste:
        raise errors.UnknownOptionError(
            "Expected copy selection to be Box, Row, or Column. "
            f"Got type {copy_selection_mode} instead."
        )

    paste_selection_mode = copy_to_paste[copy_selection_mode]
    other_selection_mode_options = [
        o for o in copy_to_paste.values() if o != paste_selection_mode
    ]

    selection_mode_options = \
        [paste_selection_mode] + other_selection_mode_options
    return selection_mode_options


def render_copy_inputs(session):
    selection_mode_options = [
        "Row",
        "Column",
        "Cell Position",
        "Rows",
        "Columns",
        "Box",
    ]
    selection_form = selection.render(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/copy.html",
            selection_form=selection_form,
    )


def render_paste_inputs(session):
    selection_mode_options = get_paste_selection_mode_options(session)
    selection_form = selection.render(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/paste.html",
            selection_form=selection_form,
    )


operation_forms = {
    "COPY": OperationForm(
        name="COPY",
        validate_and_parse=selection.validate_and_parse,
        render=render_copy_inputs,
    ),
    "PASTE": OperationForm(
        name="PASTE",
        validate_and_parse=selection.validate_and_parse,
        render=render_paste_inputs,
    ),
    "DELETE": OperationForm(
        name="DELETE",
        validate_and_parse=selection.validate_and_parse,
        render=render_delete_inputs,
    ),
    "INSERT": OperationForm(
        name="INSERT",
        validate_and_parse=validate_and_parse_insert,
        render=render_insert_inputs,
    ),
    "ERASE": OperationForm(
        name="ERASE",
        validate_and_parse=selection.validate_and_parse,
        render=render_erase_inputs,
    ),
    "VALUE": OperationForm(
        name="VALUE",
        validate_and_parse=validate_and_parse_value,
        render=render_value_inputs,
    ),
}


options = list(operation_forms.keys())
default = options[0]


def get(name):
    if name not in operation_forms:
        raise errors.UnknownOptionError(f"Unknown operation type: {name}.")
    operation_form = operation_forms[name]
    return operation_form


def render(session, operation):
    operation_form = get(operation)
    return operation_form.render(session)
