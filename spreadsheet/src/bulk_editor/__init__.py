from flask import render_template

import src.command_palette as command_palette

import src.bulk_editor.operations as operations


def render():
    show_bulk_editor = command_palette.state.get_show_bulk_editor()

    default = None
    operation_html = None

    options = operations.get_allowed_options()
    if len(options) > 0:
        default = options[0]
        operation_html = operations.render(default.value)

    return render_template(
            "partials/bulk_editor.html",
            show_bulk_editor=show_bulk_editor,
            operation=default.value if default else '',
            operation_options={
                o.value: operations.render_option(o) for o in options
            },
            operation_html=operation_html,
    )


def get_modifications(name):
    return operations.get_modifications(name)


def validate_and_parse(form):
    return operations.validate_and_parse(form)


def apply(name, modifications):
    operations.apply(name, modifications)
