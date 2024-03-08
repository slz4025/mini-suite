from flask import render_template

import src.modes as modes

import src.bulk_editor.operations as operations


def render(session):
    bulk_editor_state = modes.check(session, "Bulk-Editor")

    default = None
    operation_form = ""

    options = operations.get_allowed_options(session)
    if len(options) > 0:
        default = options[0]
        operation_form = operations.render(session, default)

    return render_template(
            "partials/bulk_editor.html",
            show_bulk_editor=bulk_editor_state,
            operation=default,
            operation_options=options,
            operation_form=operation_form,
    )


def attempt_apply(session, form):
    operations.apply(session, form)
