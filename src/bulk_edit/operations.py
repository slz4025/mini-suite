from dataclasses import dataclass
from flask import render_template
from typing import Callable

from src.errors import ClientError, UserError
from src.form import extract, parse_int, validate_nonempty
from src.sheet import (
    Input,
    InsertInput,
    ValueInput,
)

import src.bulk_edit.selection as selection


@dataclass
class OperationForm:
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
        "Rows (Indices)",
        "Columns (Indices)",
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
        "Rows (Indices)",
        "Columns (Indices)",
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
        "Rows (Indices)",
        "Columns (Indices)",
    ]
    selection_form = selection.render(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/value.html",
            value="",
            selection_form=selection_form,
    )


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
    # TODO: Have the one that matches the copy selection best first.
    selection_mode_options = [
        "Cell",
        "Row",
        "Column",
    ]
    selection_form = selection.render(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/paste.html",
            selection_form=selection_form,
    )


operation_forms = {
    "COPY": OperationForm(
        validate_and_parse=selection.validate_and_parse,
        render=render_copy_inputs,
    ),
    "PASTE": OperationForm(
        validate_and_parse=selection.validate_and_parse,
        render=render_paste_inputs,
    ),
    "DELETE": OperationForm(
        validate_and_parse=selection.validate_and_parse,
        render=render_delete_inputs,
    ),
    "INSERT": OperationForm(
        validate_and_parse=validate_and_parse_insert,
        render=render_insert_inputs,
    ),
    "ERASE": OperationForm(
        validate_and_parse=selection.validate_and_parse,
        render=render_erase_inputs,
    ),
    "VALUE": OperationForm(
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
