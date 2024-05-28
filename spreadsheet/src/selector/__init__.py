from flask import render_template

import src.command_palette.state as cp_state
import src.selector.helpers as helpers
import src.selector.inputs as inputs
import src.selector.modes as modes
import src.selector.state as state
import src.selector.types as types


def compute_from_endpoints(start, end):
    sel = helpers.compute_from_endpoints(start, end)
    mode = modes.from_selection(sel)
    return mode, sel


def compute_updated_selection(session, direction):
    sel = state.get_selection(session)
    updated_sel = helpers.compute_updated_selection(sel, direction)
    if updated_sel is None:
        return None, None

    mode = modes.from_selection(updated_sel)
    return mode, updated_sel


def validate_and_parse(session, inp):
    sel = inputs.validate_and_parse(inp)
    mode = modes.from_selection(sel)
    return mode, sel


def save(session, mode, sel):
    state.set_selection(session, sel)
    state.set_mode(session, mode)


def reset(session):
    state.reset_selection(session)
    state.reset_mode(session)


def render(session):
    show_help = cp_state.get_show_help(session)
    show_selector = cp_state.get_show_selector(session)

    mode_options = inputs.options

    mode = mode_options[0]
    selection = None
    saved_mode = state.get_mode(session)
    has_selection = saved_mode is not None
    if has_selection:
        mode = saved_mode
        selection = state.get_selection(session)

    show_adjustments = saved_mode in [
        modes.Mode.BOX,
        modes.Mode.ROWS,
        modes.Mode.COLUMNS
    ]
    show_row_adjustments = saved_mode in [
        modes.Mode.BOX,
        modes.Mode.ROWS,
    ]
    show_col_adjustments = saved_mode in [
        modes.Mode.BOX,
        modes.Mode.COLUMNS,
    ]

    inp = inputs.render(session, mode, selection)

    return render_template(
            "partials/selector.html",
            show_help=show_help,
            show_selector=show_selector,
            mode_options=[mo.value for mo in mode_options],
            mode=mode.value,
            input=inp,
            show_clear=has_selection,
            show_adjustments=show_adjustments,
            show_row_adjustments=show_row_adjustments,
            show_col_adjustments=show_col_adjustments,
    )
