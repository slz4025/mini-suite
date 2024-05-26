from flask import render_template

import src.command_palette.state as cp_state

import src.bulk_editor.operations as operations


def render(session):
    show_bulk_editor = cp_state.get_show_bulk_editor(session)

    default = None
    operation_html = None

    options = operations.get_allowed_options(session)
    if len(options) > 0:
        default = options[0]
        operation_html = operations.render(session, default.value)

    return render_template(
            "partials/bulk_editor.html",
            show_bulk_editor=show_bulk_editor,
            operation=default.value if default else '',
            operation_options={
                o.value: operations.render_option(session, o) for o in options
            },
            operation_html=operation_html,
    )


def get_modifications(session, name):
    return operations.get_modifications(session, name)


def validate_and_parse(session, form):
    return operations.validate_and_parse(session, form)


def apply(session, name, modifications):
    operations.apply(session, name, modifications)
