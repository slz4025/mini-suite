from flask import render_template

import src.modes as modes
import src.form_helpers as form_helpers

import src.data.operations as ops
import src.bulk_edit.operations as operations


def render(session):
    bulk_edit_state = modes.check(session, "Bulk-Edit")
    operation_form = operations.render(session, operations.default)

    return render_template(
            "partials/bulk_edit.html",
            show_bulk_edit=bulk_edit_state,
            operation=operations.default,
            operation_options=operations.options,
            operation_form=operation_form,
    )


def attempt_apply(session, form):
    op = form_helpers.extract(form, "operation")
    operation_form = operations.get(op)
    operation_input = operation_form.validate_and_parse(form)
    modification = ops.Modification(operation=op, input=operation_input)
    ops.apply_modification(modification)

    if operation_form.name == "COPY":
        operations.save_copy_selection_mode(session, operation_input)
