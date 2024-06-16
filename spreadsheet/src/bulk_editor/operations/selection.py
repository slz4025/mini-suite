from flask import render_template

import src.errors.types as err_types
import src.selector.state as sel_state

import src.bulk_editor.operations.state as state


def add(use, operation, selection):
    sel = operation.validate_selection(use, selection)
    state.set_selection(use, sel)


def get(name, use):
    sels = state.get_selections()
    if use not in sels:
        raise err_types.DoesNotExistError(f"{name} operation has no {use} selection.")
    sel = sels[use]
    if sel is None:
        raise err_types.DoesNotExistError("{name} operation has no {use} selection.")
    return sel


def render(name, use):
    sel = sel_state.get_selection()
    disable = sel is None
    selections = state.get_selections()

    message = "Input Selection"
    if use in selections:
        message = "✓ Selection Inputted"
    else:
        message = "Input Selection"

    return render_template(
            "partials/bulk_editor/use_selection.html",
            op=name,
            use=use,
            disable=disable,
            message=message,
    )
