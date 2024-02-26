from flask import render_template

from src.modes import check_mode
from src.sheet import (
    Modification,
    apply_modification,
)

from src.form import extract

import src.bulk_edit.operations as operations


def render(session):
    bulk_edit_state = check_mode(session, "Bulk-Edit")
    operation_form = operations.render(session, operations.default)

    return render_template(
            "partials/bulk_edit.html",
            show_bulk_edit=bulk_edit_state,
            operation=operations.default,
            operation_options=operations.options,
            operation_form=operation_form,
    )


def attempt_apply(form):
    op = extract(form, "operation")
    operation_form = operations.get(op)
    operation_input = operation_form.validate_and_parse(form)
    modification = Modification(operation=op, input=operation_input)
    apply_modification(modification)
