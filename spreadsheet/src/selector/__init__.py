from flask import render_template

import src.command_palette as command_palette

import src.selector.helpers as helpers
import src.selector.inputs as inputs
import src.selector.modes as modes
import src.selector.state as state
import src.selector.types as types


def compute_from_endpoints(start, end):
    sel = helpers.compute_from_endpoints(start, end)
    mode = modes.from_selection(sel)
    return mode, sel


def compute_updated_selection(direction):
    sel = state.get_selection()
    updated_sel = helpers.compute_updated_selection(sel, direction)
    if updated_sel is None:
        return None, None

    mode = modes.from_selection(updated_sel)
    return mode, updated_sel


def validate_and_parse(inp):
    sel = inputs.validate_and_parse(inp)
    mode = modes.from_selection(sel)
    return mode, sel


def save(mode, sel):
    state.set_selection(sel)
    state.set_mode(mode)


def reset():
    state.reset_selection()
    state.reset_mode()


def render(mode=None):
    show_help = command_palette.state.get_show_help()
    show_selector = command_palette.state.get_show_selector()

    mode_options = inputs.options

    has_selection = False
    saved_mode = None
    selection = None
    if mode is None:
        mode = mode_options[0]

        saved_mode = state.get_mode()
        has_selection = saved_mode is not None
        if has_selection:
            mode = saved_mode
            selection = state.get_selection()

    show_adjustments = saved_mode in [
        types.Mode.BOX,
        types.Mode.ROWS,
        types.Mode.COLUMNS
    ]
    show_row_adjustments = saved_mode in [
        types.Mode.BOX,
        types.Mode.ROWS,
    ]
    show_col_adjustments = saved_mode in [
        types.Mode.BOX,
        types.Mode.COLUMNS,
    ]

    inp = inputs.render(mode, selection)

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
