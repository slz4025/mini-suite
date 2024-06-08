from flask import render_template

import src.command_palette as command_palette
import src.errors.types as err_types
import src.sheet as sheet
import src.selector.state as sel_state
import src.selector.types as sel_types

import src.viewer.state as state


def get_selection():
    sel = sel_state.get_selection()
    if isinstance(sel, sel_types.CellPosition):
        return sel
    elif isinstance(sel, sel_types.RowIndex):
        return sel
    elif isinstance(sel, sel_types.ColIndex):
        return sel
    elif isinstance(sel, sel_types.Box):
        if sel.row_range.end.value - sel.row_range.start.value == 1 \
                and sel.col_range.end.value - sel.col_range.start.value == 1:
            sel = sel_types.CellPosition(
                row_index=sel_types.RowIndex(sel.row_range.start.value),
                col_index=sel_types.ColIndex(sel.col_range.start.value),
            )
        return sel
    elif isinstance(sel, sel_types.RowRange):
        if sel.end.value - sel.start.value == 1:
            sel = sel_types.RowIndex(sel.start.value)
        return sel
    elif isinstance(sel, sel_types.ColRange):
        if sel.end.value - sel.start.value == 1:
            sel = sel_types.ColIndex(sel.start.value)
        return sel
    else:
        return None


def set():
    bounds = sheet.data.get_bounds()

    upperleft = state.get_upperleft()
    row_start = upperleft.row_index.value
    col_start = upperleft.col_index.value

    nrows, ncols = state.get_dimensions()

    selection = get_selection()
    if isinstance(selection, sel_types.CellPosition):
        # put cell in center of port
        row = selection.row_index.value
        row_end = min(row + (nrows) // 2 + 1, bounds.row.value)
        row_start = max(0, row_end - nrows)

        col = selection.col_index.value
        col_end = min(col + (ncols) // 2 + 1, bounds.col.value)
        col_start = max(0, col_end - ncols)
    elif isinstance(selection, sel_types.RowIndex):
        # put row in center of port
        row = selection.value
        row_end = min(row + (nrows) // 2 + 1, bounds.row.value)
        row_start = max(0, row_end - nrows)
    elif isinstance(selection, sel_types.ColIndex):
        # put column in center of port
        col = selection.value
        col_end = min(col + (ncols) // 2 + 1, bounds.col.value)
        col_start = max(0, col_end - ncols)
    elif isinstance(selection, sel_types.Box):
        # constrain port to given box
        row_start = selection.row_range.start.value
        col_start = selection.col_range.start.value

        nrows = selection.row_range.end.value - selection.row_range.start.value
        ncols = selection.col_range.end.value - selection.col_range.start.value
    elif isinstance(selection, sel_types.RowRange):
        # constrain port to given rows
        row_start = selection.start.value
        nrows = selection.end.value - selection.start.value
    elif isinstance(selection, sel_types.ColRange):
        # constrain port to given columns
        col_start = selection.start.value
        ncols = selection.end.value - selection.start.value
    else:
        raise err_types.NotSupportedError("Need a valid selection to target.")

    state.set_upperleft(sel_types.CellPosition(
        row_index=sel_types.RowIndex(row_start),
        col_index=sel_types.RowIndex(col_start),
    ))
    state.set_dimensions(nrows, ncols)


def render():
    show_help = command_palette.state.get_show_help()
    target = get_selection()

    show_target = target is not None

    return render_template(
            "partials/viewer/target.html",
            show_help=show_help,
            show_target=show_target,
    )
