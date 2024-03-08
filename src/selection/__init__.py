from flask import render_template
import os

import src.form_helpers as form_helpers
import src.modes as modes

import src.selection.inputs as inputs
import src.selection.state as state


def save(session, inp):
    sel = inputs.validate_and_parse(inp)
    state.set_selection(session, sel)

    mode = form_helpers.extract(inp, "mode", name="selection mode")
    state.set_mode(session, mode)


def render_inputs(session, mode):
    help_state = modes.check(session, "Help")
    form = inputs.get_form(mode)
    template_path = os.path.join(
        "partials/selection",
        form.template,
    )
    html = render_template(template_path, show_help=help_state)
    return html


def render(session):
    help_state = modes.check(session, "Help")
    selection_state = modes.check(session, "Selection")

    mode_options = inputs.options
    default_mode = mode_options[0]
    inp = render_inputs(session, default_mode)

    return render_template(
            "partials/selection.html",
            show_help=help_state,
            show_selection=selection_state,
            mode=default_mode,
            mode_options=mode_options,
            input=inp,
    )
