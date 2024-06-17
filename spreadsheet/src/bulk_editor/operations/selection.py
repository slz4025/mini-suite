from flask import render_template

import src.errors.types as err_types
import src.selector.state as sel_state
import src.selector.types as sel_types

import src.bulk_editor.operations.state as state


def convert_to_target(sel):
    if isinstance(sel, sel_types.RowIndex):
        target = sel
    elif isinstance(sel, sel_types.ColIndex):
        target = sel
    elif isinstance(sel, sel_types.CellPosition):
        target = sel
    elif isinstance(sel, sel_types.RowRange):
        if sel.end.value - sel.start.value == 1:
            target = sel_types.RowIndex(sel.start.value)
        else:
            sel_type = type(sel)
            raise err_types.NotSupportedError(
                f"Could not convert selection of type {sel_type} to target. "
                "Select a single row instead."
            )
    elif isinstance(sel, sel_types.ColRange):
        if sel.end.value - sel.start.value == 1:
            target = sel_types.ColIndex(sel.start.value)
        else:
            sel_type = type(sel)
            raise err_types.NotSupportedError(
                f"Could not convert selection of type {sel_type} to target. "
                "Select a single column instead."
            )
    elif isinstance(sel, sel_types.Box):
        if sel.row_range.end.value - sel.row_range.start.value == 1 \
                and sel.col_range.end.value - sel.col_range.start.value == 1:
            target = sel_types.CellPosition(
                row_index=sel_types.RowIndex(sel.row_range.start.value),
                col_index=sel_types.ColIndex(sel.col_range.start.value),
            )
        else:
            sel_type = type(sel)
            raise err_types.NotSupportedError(
                f"Could not convert selection of type {sel_type} to target. "
                "Select a single cell instead."
            )
    else:
        sel_type = type(sel)
        raise err_types.NotSupportedError(
            f"Could not convert selection of type {sel_type} to target."
        )
    return target


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
