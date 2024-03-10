from flask import render_template
import os

import src.form_helpers as form_helpers
import src.modes as modes
import src.errors as errors

import src.selection.helpers as helpers
import src.selection.inputs as inputs
import src.selection.state as state
import src.selection.types as types


def compute_from_endpoints(start, end):
    return helpers.compute_from_endpoints(start, end)


def validate_and_parse(session, inp):
    mode = form_helpers.extract(inp, "mode", name="selection mode")
    sel = inputs.validate_and_parse(inp)
    return mode, sel


def save(session, mode, sel):
    state.set_selection(session, sel)
    state.set_mode(session, mode)


def render_inputs(session, mode, sel=None):
    help_state = modes.check(session, "Help")

    row_index = ""
    col_index = ""
    row_start = ""
    row_end = ""
    col_start = ""
    col_end = ""

    if sel is not None:
        if isinstance(sel, types.RowIndex):
            row_index = sel.value
        elif isinstance(sel, types.ColIndex):
            col_index = sel.value
        elif isinstance(sel, types.CellPosition):
            row_index = sel.row_index.value
            col_index = sel.col_index.value
        elif isinstance(sel, types.RowRange):
            row_start = sel.start.value
            row_end = sel.end.value
        elif isinstance(sel, types.ColRange):
            col_start = sel.start.value
            col_end = sel.end.value
        elif isinstance(sel, types.Box):
            row_start = sel.row_range.start.value
            row_end = sel.row_range.end.value
            col_start = sel.col_range.start.value
            col_end = sel.col_range.end.value
        else:
            sel_type = type(sel)
            raise errors.UnknownOptionError(
                f"Unknown selection type: {sel_type}."
            )

    form = inputs.get_form(mode)
    template_path = os.path.join(
        "partials/selection",
        form.template,
    )
    html = render_template(
        template_path,
        show_help=help_state,
        row_index=row_index,
        col_index=col_index,
        row_start=row_start,
        row_end=row_end,
        col_start=col_start,
        col_end=col_end,
    )
    return html


def render(session):
    help_state = modes.check(session, "Help")
    selection_state = modes.check(session, "Selection")

    mode_options = inputs.options

    mode = mode_options[0]
    selection = None
    saved_mode = state.get_mode(session)
    if saved_mode is not None:
        mode = saved_mode
        selection = state.get_selection(session)

    inp = render_inputs(session, mode, selection)

    return render_template(
            "partials/selection.html",
            show_help=help_state,
            show_selection=selection_state,
            mode_options=mode_options,
            mode=mode,
            input=inp,
    )
