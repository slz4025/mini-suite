from dataclasses import dataclass
from flask import render_template
import os
from typing import Callable

import src.errors as errors
import src.form_helpers as form_helpers
import src.modes as modes

import src.bulk_editor.selection_inputs as inputs
import src.data.selections as selections


@dataclass
class SelectionForm:
    name: str
    template: str
    validate_and_parse: Callable[[object], selections.Selection]


selection_forms = {
    "Row": SelectionForm(
        name="Row",
        template="row_index.html",
        validate_and_parse=inputs.get_row_index,
    ),
    "Column": SelectionForm(
        name="Column",
        template="col_index.html",
        validate_and_parse=inputs.get_col_index,
    ),
    "Cell Position": SelectionForm(
        name="Cell Position",
        template="cell_position.html",
        validate_and_parse=inputs.get_cell_position,
    ),
    "Rows": SelectionForm(
        name="Rows",
        template="row_range.html",
        validate_and_parse=inputs.get_row_range,
    ),
    "Columns": SelectionForm(
        name="Columns",
        template="col_range.html",
        validate_and_parse=inputs.get_col_range,
    ),
    "Box": SelectionForm(
        name="Box",
        template="box.html",
        validate_and_parse=inputs.get_box,
    ),
}


def get(name):
    if name in selection_forms:
        return selection_forms[name]
    else:
        raise errors.UnknownOptionError(f"Unknown selection type: {name}.")


def validate_and_parse(form):
    mode = form_helpers.extract(form, "selection-mode", name="selection mode")
    selection_form = get(mode)
    selection = selection_form.validate_and_parse(form)
    return selection


def render_inputs(session, mode):
    help_state = modes.check(session, "Help")
    selection_form = selection_forms.get(mode)
    template_path = os.path.join(
        "partials/bulk_editor/selection",
        selection_form.template,
    )
    html = render_template(template_path, show_help=help_state)
    return html


def render(session, selection_mode_options):
    help_state = modes.check(session, "Help")
    default_selection_mode = selection_mode_options[0]
    selection_inputs = render_inputs(session, default_selection_mode)
    return render_template(
            "partials/bulk_editor/selection.html",
            selection_mode=default_selection_mode,
            selection_mode_options=selection_mode_options,
            selection_inputs=selection_inputs,
            show_help=help_state,
    )
