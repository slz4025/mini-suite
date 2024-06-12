from flask import render_template

import src.command_palette as command_palette

import src.bulk_editor.operations as operations


def render():
    show_help = command_palette.state.get_show_help()
    show_bulk_editor = command_palette.state.get_show_bulk_editor()

    operation_html = None

    options = operations.get_all()
    operation = operations.state.get_current_operation()
    operation_html = operations.render(operation)

    return render_template(
            "partials/bulk_editor.html",
            show_help=show_help,
            show_bulk_editor=show_bulk_editor,
            operation=operation.value,
            operation_options=[
                o.value for o in options
            ],
            operation_html=operation_html,
    )


def apply_operation(name):
    name, modifications = operations.get_modifications(name)
    operations.apply(name, modifications)


def apply(name, form):
    modifications = operations.validate_and_parse(name, form)
    operations.apply(name, modifications)
