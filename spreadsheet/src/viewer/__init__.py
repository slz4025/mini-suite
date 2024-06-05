from flask import render_template

import src.command_palette as command_palette
import src.errors.types as err_types
import src.sheet as sheet
import src.selector.types as sel_types

import src.viewer.state as state
import src.viewer.target as target


def in_view(cell_position):
    upperleft = state.get_upperleft()
    nrows, ncols = state.get_dimensions()

    start_row = upperleft.row_index.value
    start_col = upperleft.col_index.value

    end_row = start_row + nrows
    end_col = start_col + ncols

    row = cell_position.row_index.value
    col = cell_position.col_index.value

    return (row >= start_row and row < end_row) \
        and (col >= start_col and col < end_col)


def move_upperleft(method):
    upperleft = state.get_upperleft()
    mrows, mcols = state.get_move_increments()

    if method == 'home':
        moved = sel_types.CellPosition(
            row_index=sel_types.RowIndex(0),
            col_index=sel_types.ColIndex(0),
        )
    else:
        delta_row = 0
        delta_col = 0
        match method:
            case 'up':
                delta_row = -mrows
            case 'down':
                delta_row = mrows
            case 'left':
                delta_col = -mcols
            case 'right':
                delta_col = mcols
            case _:
                raise err_types.UnknownOptionError(
                    f"Unexpected method: {method}."
                )

        bounds = sheet.data.get_bounds()

        row = upperleft.row_index.value
        potential_row = max(0, upperleft.row_index.value+delta_row)
        if potential_row < bounds.row.value:
            row = potential_row

        col = upperleft.col_index.value
        potential_col = max(0, upperleft.col_index.value+delta_col)
        if potential_col < bounds.col.value:
            col = potential_col

        moved = sel_types.CellPosition(
            row_index=sel_types.RowIndex(row),
            col_index=sel_types.ColIndex(col),
        )

    state.set_upperleft(moved)


def render(session):
    show_help = command_palette.state.get_show_help()
    show_viewer = command_palette.state.get_show_viewer()
    mrows, mcols = state.get_move_increments()
    nrows, ncols = state.get_dimensions()

    target_html = target.render(session)

    return render_template(
            "partials/viewer.html",
            show_help=show_help,
            show_viewer=show_viewer,
            mrows=mrows,
            mcols=mcols,
            nrows=nrows,
            ncols=ncols,
            target=target_html,
    )
