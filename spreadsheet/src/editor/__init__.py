from flask import render_template

import src.errors as errors
import src.command_palette as command_palette
import src.navigator as navigator
import src.sheet as sheet
import src.selection.modes as sel_modes
import src.selection.types as sel_types

import src.editor.state as state


def render(session, op=None):
    show_help = command_palette.get_show_help(session)
    show_editor = command_palette.get_show_editor(session)

    focused_cell = state.get_focused_cell_position(session)
    if focused_cell is not None:
        try:
            sel_types.check_cell_position(focused_cell)
        except errors.OutOfBoundsError:
            state.reset_focused_cell_position(session)
            focused_cell = None

    if focused_cell is not None:
        if not navigator.in_view(session, focused_cell):
            state.reset_focused_cell_position(session)
            focused_cell = None

    row = None
    col = None
    data = None
    editing = focused_cell is not None

    if editing:
        row = focused_cell.row_index.value
        col = focused_cell.col_index.value
        data = sheet.get_cell_value(focused_cell)

    return render_template(
        "partials/editor.html",
        show_help=show_help,
        show_editor=show_editor,
        editing=editing,
        row=row if row is not None else "",
        col=col if col is not None else "",
        data=data if data is not None else "",
    )
