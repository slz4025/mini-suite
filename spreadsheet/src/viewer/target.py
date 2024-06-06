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


def set():
    nrows, ncols = state.get_dimensions()

    selection_mode = sel_state.get_mode()
    selection = get_selection()
    if selection is None:
        raise err_types.NotSupportedError(
            "Centering requires a cell position selection. "
            f"Got selection mode {selection_mode.value} instead."
        )

    row = selection.row_index.value
    col = selection.col_index.value

    bounds = sheet.data.get_bounds()
    row_end = min(row + (nrows) // 2 + 1, bounds.row.value)
    col_end = min(col + (ncols) // 2 + 1, bounds.col.value)
    row_start = max(0, row_end - nrows)
    col_start = max(0, col_end - ncols)

    state.set_upperleft(sel_types.CellPosition(
        row_index=sel_types.RowIndex(row_start),
        col_index=sel_types.RowIndex(col_start),
    ))


def render():
    show_help = command_palette.state.get_show_help()
    target = get_selection()

    show_target = False
    row = None
    col = None
    if target is not None:
        show_target = True
        row = target.row_index.value
        col = target.col_index.value

    return render_template(
            "partials/viewer/target.html",
            show_help=show_help,
            show_target=show_target,
            row=row,
            col=col,
    )
