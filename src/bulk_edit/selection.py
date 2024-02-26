from dataclasses import dataclass
from flask import render_template
import os
from typing import Callable

from src.errors import ClientError
from src.form import extract
from src.modes import check_mode
from src.sheet import (
    Selection,
)

import src.bulk_edit.selection_inputs as inputs


@dataclass
class SelectionForm:
    name: str
    template: str
    validate_and_parse: Callable[[object], Selection]


selection_forms = {
    "Cell": SelectionForm(
        name="Cell",
        template="cell.html",
        validate_and_parse=inputs.cell,
    ),
    "Box": SelectionForm(
        name="Box",
        template="box.html",
        validate_and_parse=inputs.box,
    ),
    "Row": SelectionForm(
        name="Row",
        template="index.html",
        validate_and_parse=inputs.row_index,
    ),
    "Column": SelectionForm(
        name="Column",
        template="index.html",
        validate_and_parse=inputs.col_index,
    ),
    "Rows (Range)": SelectionForm(
        name="Rows (Range)",
        template="range.html",
        validate_and_parse=inputs.row_range,
    ),
    "Columns (Range)": SelectionForm(
        name="Columns (Range)",
        template="range.html",
        validate_and_parse=inputs.col_range,
    ),
    "Rows (Indices)": SelectionForm(
        name="Rows (Indices)",
        template="indices.html",
        validate_and_parse=inputs.row_indices,
    ),
    "Columns (Indices)": SelectionForm(
        name="Columns (Indices)",
        template="indices.html",
        validate_and_parse=inputs.col_indices,
    ),
}


def get(name):
    if name in selection_forms:
        return selection_forms[name]
    else:
        raise ClientError(f"Unknown selection type: {name}.")


def validate_and_parse(form):
    mode = extract(form, "selection-mode", name="selection mode")
    selection_form = get(mode)
    selection = selection_form.validate_and_parse(form)
    return selection


def render_inputs(session, mode):
    help_state = check_mode(session, "Help")
    selection_form = selection_forms.get(mode)
    template_path = os.path.join(
        "partials/bulk_edit/selection",
        selection_form.template,
    )
    html = render_template(template_path, show_help=help_state)
    return html


def render(session, selection_mode_options):
    help_state = check_mode(session, "Help")
    default_selection_mode = selection_mode_options[0]
    selection_inputs = render_inputs(session, default_selection_mode)
    return render_template(
            "partials/bulk_edit/selection.html",
            selection_mode=default_selection_mode,
            selection_mode_options=selection_mode_options,
            selection_inputs=selection_inputs,
            show_help=help_state,
    )
