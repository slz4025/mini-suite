from flask import render_template

import src.errors as errors
import src.settings as settings

import src.data.operations as operations
import src.selection.state as sel_state
import src.selection.types as sel_types
import src.data.sheet as sheet


def get_focused_cell_position(session):
    return sel_types.CellPosition(
        row_index=sel_types.RowIndex(
            int(session["focused-cell-position"]["row-index"])
        ),
        col_index=sel_types.ColIndex(
            int(session["focused-cell-position"]["col-index"])
        ),
    )


def set_focused_cell_position(session, focused_cell_position):
    session["focused-cell-position"] = {
        "row-index": str(focused_cell_position.row_index.value),
        "col-index": str(focused_cell_position.col_index.value),
    }


def is_editing(session, cell_position):
    focused_cell_position = get_focused_cell_position(session)
    return focused_cell_position.equals(cell_position)


def make_render_selected(session):
    sel = sel_state.get_selection(session)

    if isinstance(sel, sel_types.RowIndex):
        row_index = sel_types.RowIndex(sel.value - 1)

        def render_selected(cp): return "selected-next-row" \
            if row_index.equals(cp.row_index) else ""
    elif isinstance(sel, sel_types.ColIndex):
        col_index = sel_types.ColIndex(sel.value - 1)

        def render_selected(cp): return "selected-next-col" \
            if col_index.equals(cp.col_index) else ""
    elif isinstance(sel, sel_types.CellPosition):
        cell_position = sel_types.CellPosition(
            row_index=sel_types.RowIndex(sel.row_index.value - 1),
            col_index=sel_types.ColIndex(sel.col_index.value - 1),
        )

        def render_selected(cp): return "selected-bottomright" \
            if cell_position.equals(cp) else ""
    elif isinstance(sel, sel_types.RowRange):
        start_row, end_row, start_col, end_col = \
            sel_types.get_bounds_from_selection(sel)

        def render_selected(cp): return "selected-current" \
            if cp.in_bounds(start_row, end_row, start_col, end_col) else ""
    elif isinstance(sel, sel_types.ColRange):
        start_row, end_row, start_col, end_col = \
            sel_types.get_bounds_from_selection(sel)

        def render_selected(cp): return "selected-current" \
            if cp.in_bounds(start_row, end_row, start_col, end_col) else ""
    elif isinstance(sel, sel_types.Box):
        start_row, end_row, start_col, end_col = \
            sel_types.get_bounds_from_selection(sel)

        def render_selected(cp): return "selected-current" \
            if cp.in_bounds(start_row, end_row, start_col, end_col) else ""
    else:
        def render_selected(cp): return ""

    return render_selected


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


def set_center(session):
    current_settings = settings.get(session)
    nrows = current_settings.nrows
    ncols = current_settings.ncols

    selection_mode = sel_state.get_mode(session)
    selection = sel_state.get_selection(session)
    if not isinstance(selection, sel_types.CellPosition):
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


def init(session):
    upperleft = sel_types.CellPosition(
        row_index=sel_types.RowIndex(0),
        col_index=sel_types.ColIndex(0),
    )
    set_upperleft(session, upperleft)
    focused_cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(0),
        col_index=sel_types.ColIndex(0),
    )
    set_focused_cell_position(session, focused_cell_position)


def render_cell(session, cell_position, editing=False, render_selected=None):
    sel_types.check_cell_position(cell_position)

    renders = []
    input_render = None
    if render_selected is None:
        render_selected = make_render_selected(session)
    render_selected_state = render_selected(cell_position)
    if "selected-current" in render_selected_state:
        input_render = "selected"
    renders.append(render_selected_state)
    # Apply later so takes precendence.
    if editing and is_editing(session, cell_position):
        renders.append("editing-current")
        input_render = "editing"

    value = operations.get_cell(cell_position)
    if value is None:
        value = ""

    return render_template(
            "partials/port/cell.html",
            row=cell_position.row_index.value,
            col=cell_position.col_index.value,
            data=value,
            renders=renders,
            input_render=input_render if input_render is not None else '',
    )


def render_corner_header(session, render_selected=None):
    cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(-1),
        col_index=sel_types.ColIndex(-1),
    )

    renders = []
    if render_selected is None:
        render_selected = make_render_selected(session)
    render_selected_state = render_selected(cell_position)
    renders.append(render_selected_state)

    return render_template(
        "partials/port/corner_header.html",
        data="",
        renders=renders,
    )


def render_row_header(session, row_index, render_selected=None):
    cell_position = sel_types.CellPosition(
        row_index=row_index,
        col_index=sel_types.ColIndex(-1),
    )

    renders = []
    if render_selected is None:
        render_selected = make_render_selected(session)
    render_selected_state = render_selected(cell_position)
    renders.append(render_selected_state)

    return render_template(
        "partials/port/row_header.html",
        index=row_index.value,
        data=row_index.value,
        renders=renders,
    )


def render_col_header(session, col_index, render_selected=None):
    cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(-1),
        col_index=col_index,
    )

    renders = []
    if render_selected is None:
        render_selected = make_render_selected(session)
    render_selected_state = render_selected(cell_position)
    renders.append(render_selected_state)

    return render_template(
        "partials/port/col_header.html",
        index=col_index.value,
        data=col_index.value,
        renders=renders,
    )


def render_row(session, leftmost, ncols, bounds, render_selected):
    header = render_row_header(
        session,
        leftmost.row_index,
        render_selected=render_selected,
    )

    cells = []
    for col in range(
        leftmost.col_index.value,
        min(leftmost.col_index.value+ncols, bounds.col.value)
    ):
        cell = render_cell(
            session,
            sel_types.CellPosition(
                row_index=leftmost.row_index,
                col_index=sel_types.ColIndex(col),
            ),
            render_selected=render_selected,
        )
        cells.append(cell)

    return render_template(
            "partials/port/row.html",
            header=header,
            data="\n".join(cells),
    )


def render_table_header(
    session,
    upperleft,
    ncols,
    bounds,
    render_selected,
):
    corner = render_corner_header(session, render_selected=render_selected)

    header = []
    for col in range(
        upperleft.col_index.value,
        min(upperleft.col_index.value+ncols, bounds.col.value)
    ):
        h = render_col_header(
            session,
            sel_types.ColIndex(col),
            render_selected=render_selected,
        )
        header.append(h)

    return render_template(
            "partials/port/row.html",
            header=corner,
            data="\n".join(header),
    )


def render_table(
    session,
    upperleft,
    nrows,
    ncols,
    bounds,
):
    render_selected = make_render_selected(session)

    header = render_table_header(
        session,
        upperleft,
        ncols,
        bounds,
        render_selected,
    )

    tablerows = []
    for row in range(
        upperleft.row_index.value,
        min(upperleft.row_index.value+nrows, bounds.row.value)
    ):
        tablerow = render_row(
            session,
            sel_types.CellPosition(
                row_index=sel_types.RowIndex(row),
                col_index=upperleft.col_index,
            ),
            ncols,
            bounds,
            render_selected,
        )
        tablerows.append(tablerow)

    return render_template(
            "partials/port/table.html",
            data="\n".join(tablerows),
            header=header,
    )


def render(session):
    upperleft = get_upperleft(session)
    current_settings = settings.get(session)
    bounds = sheet.get_bounds()

    table = render_table(
        session,
        upperleft=upperleft,
        nrows=current_settings.nrows,
        ncols=current_settings.ncols,
        bounds=bounds,
    )
    return table
