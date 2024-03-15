from flask import render_template

import src.modes as modes
import src.selection.state as sel_state
import src.selection.types as sel_types


def render_center(session):
    help_state = modes.check(session, "Help")

    selection = sel_state.get_selection(session)
    show_center = isinstance(selection, sel_types.CellPosition)

    return render_template(
            "partials/navigator/center.html",
            show_help=help_state,
            show_center=show_center,
    )


def render(session):
    help_state = modes.check(session, "Help")
    navigator_state = modes.check(session, "Navigator")
    center = render_center(session)
    return render_template(
            "partials/navigator.html",
            show_help=help_state,
            show_navigator=navigator_state,
            center=center,
    )
