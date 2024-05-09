from flask import render_template

import src.command_palette as command_palette
import src.errors as errors
import src.sheet as sheet
import src.selection.state as sel_state
import src.selection.types as sel_types


def get_upperleft(session):
    return sel_types.CellPosition(
        row_index=sel_types.RowIndex(int(session["upper-left"]["row-index"])),
        col_index=sel_types.ColIndex(int(session["upper-left"]["col-index"])),
    )


def set_upperleft(session, upperleft):
    session["upper-left"] = {
        "row-index": str(upperleft.row_index.value),
        "col-index": str(upperleft.col_index.value),
    }


def get_dimensions(session):
    nrows = int(session["dimensions"]["nrows"])
    ncols = int(session["dimensions"]["ncols"])
    return nrows, ncols


def set_dimensions(session, nrows, ncols):
    session["dimensions"] = {
        "nrows": str(nrows),
        "ncols": str(ncols),
    }


def get_move_increments(session):
    mrows = int(session["move-increments"]["mrows"])
    mcols = int(session["move-increments"]["mcols"])
    return mrows, mcols


def set_move_increments(session, mrows, mcols):
    session["move-increments"] = {
        "mrows": str(mrows),
        "mcols": str(mcols),
    }


def get_selection_for_target(session):
    sel = sel_state.get_selection(session)
    if isinstance(sel, sel_types.CellPosition):
        return sel
    elif isinstance(sel, sel_types.Box):
        if sel.row_range.end.value - sel.row_range.start.value == 1 \
                and sel.col_range.end.value - sel.col_range.start.value == 1:
            sel = sel_types.CellPosition(
                row_index=sel_types.RowIndex(sel.row_range.start.value),
                col_index=sel_types.ColIndex(sel.col_range.start.value),
            )
            return sel
        return None
    else:
        return None


def set_target(session):
    nrows, ncols = get_dimensions(session)

    selection_mode = sel_state.get_mode(session)
    selection = get_selection_for_target(session)
    if selection is None:
        raise errors.NotSupportedError(
            "Centering requires a cell position selection. "
            f"Got selection mode {selection_mode.value} instead."
        )

    row = selection.row_index.value
    col = selection.col_index.value

    bounds = sheet.get_bounds()
    row_end = min(row + (nrows) // 2 + 1, bounds.row.value)
    col_end = min(col + (ncols) // 2 + 1, bounds.col.value)
    row_start = max(0, row_end - nrows)
    col_start = max(0, col_end - ncols)

    upperleft = sel_types.CellPosition(
        row_index=sel_types.RowIndex(row_start),
        col_index=sel_types.RowIndex(col_start),
    )
    set_upperleft(session, upperleft)


def in_view(session, cell_position):
    upperleft = get_upperleft(session)
    start_row = upperleft.row_index.value
    start_col = upperleft.col_index.value

    nrows, ncols = get_dimensions(session)
    end_row = start_row + nrows
    end_col = start_col + ncols

    row = cell_position.row_index.value
    col = cell_position.col_index.value

    return (row >= start_row and row < end_row) \
        and (col >= start_col and col < end_col)


def move_upperleft(session, method):
    mrows, mcols = get_move_increments(session)

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
                raise errors.UnknownOptionError(
                    f"Unexpected method: {method}."
                )

        upperleft = get_upperleft(session)
        bounds = sheet.get_bounds()

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

    set_upperleft(session, moved)


def render_target(session):
    show_help = command_palette.get_show_help(session)
    target = get_selection_for_target(session)

    show_target = False
    row = None
    col = None
    if target is not None:
        show_target = True
        row = target.row_index.value
        col = target.col_index.value

    return render_template(
            "partials/navigator/target.html",
            show_help=show_help,
            show_target=show_target,
            row=row,
            col=col,
    )


def render(session):
    show_help = command_palette.get_show_help(session)
    show_navigator = command_palette.get_show_navigator(session)
    nrows, ncols = get_dimensions(session)
    mrows, mcols = get_move_increments(session)
    target = render_target(session)
    return render_template(
            "partials/navigator.html",
            show_help=show_help,
            show_navigator=show_navigator,
            mrows=mrows,
            mcols=mcols,
            nrows=nrows,
            ncols=ncols,
            target=target,
    )


def init(session):
    upperleft = sel_types.CellPosition(
        row_index=sel_types.RowIndex(0),
        col_index=sel_types.ColIndex(0),
    )
    set_upperleft(session, upperleft)

    nrows = 15
    ncols = 15
    set_dimensions(session, nrows, ncols)

    mrows = 5
    mcols = 5
    set_move_increments(session, mrows, mcols)
