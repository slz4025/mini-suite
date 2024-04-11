from flask import render_template

import src.command_palette as command_palette
import src.errors as errors
import src.selection.helpers as helpers
import src.selection.inputs as inputs
import src.selection.modes as modes
import src.selection.state as state
import src.selection.types as types


def compute_from_endpoints(start, end):
    sel = helpers.compute_from_endpoints(start, end)
    mode = modes.from_selection(sel)
    return mode, sel


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
    show_help = command_palette.get_show_help(session)
    show_selection = command_palette.get_show_selection(session)

    mode_options = inputs.options

    mode = mode_options[0]
    selection = None
    saved_mode = state.get_mode(session)
    has_selection = saved_mode is not None
    if has_selection:
        mode = saved_mode
        selection = state.get_selection(session)

    inp = inputs.render(session, mode, selection)

    return render_template(
            "partials/selection.html",
            show_help=show_help,
            show_selection=show_selection,
            mode_options=[mo.value for mo in mode_options],
            mode=mode.value,
            input=inp,
            show_clear=has_selection,
    )
