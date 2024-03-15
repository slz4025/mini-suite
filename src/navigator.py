from flask import render_template

import src.errors as errors
import src.data.sheet as sheet
import src.modes as modes
import src.settings as settings
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
    current_settings = settings.get(session)
    nrows = current_settings.nrows
    ncols = current_settings.ncols

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


def move_upperleft(session, method):
    current_settings = settings.get(session)
    mrows = current_settings.mrows
    mcols = current_settings.mcols

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
    help_state = modes.check(session, "Help")
    show_target = get_selection_for_target(session) is not None

    return render_template(
            "partials/navigator/target.html",
            show_help=help_state,
            show_target=show_target,
    )


def render(session):
    help_state = modes.check(session, "Help")
    navigator_state = modes.check(session, "Navigator")
    target = render_target(session)
    return render_template(
            "partials/navigator.html",
            show_help=help_state,
            show_navigator=navigator_state,
            target=target,
    )


def init(session):
    upperleft = sel_types.CellPosition(
        row_index=sel_types.RowIndex(0),
        col_index=sel_types.ColIndex(0),
    )
    set_upperleft(session, upperleft)
