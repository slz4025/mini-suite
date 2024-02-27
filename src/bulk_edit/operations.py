from dataclasses import dataclass
from flask import render_template
from typing import Callable

from src.errors import ClientError, UserError
from src.form import extract, parse_int, validate_nonempty
from src.sheet import (
    Axis,
    BoxSelection,
    RangeSelection,
    Selection,
    Input,
    InsertInput,
    ValueInput,
)

import src.bulk_edit.selection as selection
import src.bulk_edit.state as state


@dataclass
class OperationForm:
    name: str
    validate_and_parse: Callable[[object], Input]
    render: Callable[[], str]


def validate_and_parse_insert(form):
    sel = selection.validate_and_parse(form)

    number = extract(form, "insert-number", name="number")
    validate_nonempty(number, name="number")
    number = parse_int(number, name="number")

    return InsertInput(
        selection=sel,
        number=number,
    )


def validate_and_parse_value(form):
    sel = selection(form)

    value = extract(form, "value", name="value")
    if value == "":
        raise UserError("Field 'value' was not given.")

    return ValueInput(selection=sel, value=value)


def render_delete_inputs(session):
    selection_mode_options = [
        "Rows (Range)",
        "Columns (Range)",
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
        "Box",
        "Rows (Range)",
        "Columns (Range)",
    ]
    selection_form = selection.render(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/erase.html",
            selection_form=selection_form,
    )


def render_value_inputs(session):
    selection_mode_options = [
        "Box",
        "Rows (Range)",
        "Columns (Range)",
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
    if isinstance(operation_input, BoxSelection):
        selection_mode = "Box"
    elif isinstance(operation_input, RangeSelection):
        match operation_input.axis:
            case Axis.ROW:
                selection_mode = "Row (Range)"
            case Axis.COLUMN:
                selection_mode = "Column (Range)"
    elif isinstance(operation_input, Selection):
        raise ClientError(
            "Expected copy selection to be Box, Row, or Column. "
            f"Got type {input_type} instead."
        )
    else:
        raise ClientError(
            f"Expected copy input to be a selection. "
            f"Got type {input_type} instead."
        )

    assert selection_mode is not None
    state.set_buffer_selection_mode(session, selection_mode)


def get_paste_selection_mode_options(session):
    copy_to_paste = {
        "Box": "Cell",
        "Row (Range)": "Row",
        "Column (Range)": "Column",
    }
    copy_selection_mode = state.get_buffer_selection_mode(session)
    if copy_selection_mode is None:
        raise UserError("Did not copy anything yet to paste.")
    if copy_selection_mode not in copy_to_paste:
        raise ClientError(
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
        "Box",
        "Rows (Range)",
        "Columns (Range)",
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
        raise ClientError(f"Unknown operation type: {name}.")
    operation_form = operation_forms[name]
    return operation_form


def render(session, operation):
    operation_form = get(operation)
    return operation_form.render(session)
