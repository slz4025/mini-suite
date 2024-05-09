from flask import render_template

import src.computer as computer
import src.editor.state as ed_state
import src.errors as errors
import src.navigator as navigator
import src.selection.state as sel_state
import src.selection.types as sel_types
import src.sheet as sheet


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


def render_cell(
    session,
    cell_position,
    render_selected=None,
    compute=True,
    catch_failure=False,
):
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
    if ed_state.is_editing(session, cell_position):
        renders.append("editing-current")
        input_render = "editing"

    try:
        value = computer.get_cell_computed(
            cell_position,
            use_cache=not compute,
        )
    except errors.UserError as e:
        if catch_failure:
            # set as empty while report error
            value = ""
            renders.append("failure")
        else:
            raise e

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


def render_row(
    session,
    leftmost,
    ncols,
    bounds,
    render_selected,
    min_height="100",
    compute=True,
    catch_failure=False,
):
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
            compute=compute,
            catch_failure=catch_failure,
        )
        cells.append(cell)

    return render_template(
            "partials/port/row.html",
            header=header,
            data="\n".join(cells),
            height=f"{min_height}%",
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
            height="1rem",
    )


def render_table(
    session,
    upperleft,
    nrows,
    ncols,
    bounds,
    compute=True,
    catch_failure=False,
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
            min_height=100.0 / float(nrows + 1),
            compute=compute,
            catch_failure=catch_failure,
        )
        tablerows.append(tablerow)

    return render_template(
            "partials/port/table.html",
            data="\n".join(tablerows),
            header=header,
    )


def render(session, compute=True, catch_failure=False):
    upperleft = navigator.get_upperleft(session)
    nrows, ncols = navigator.get_dimensions(session)
    bounds = sheet.get_bounds()

    table = render_table(
        session,
        upperleft=upperleft,
        nrows=nrows,
        ncols=ncols,
        bounds=bounds,
        compute=compute,
        catch_failure=catch_failure,
    )
    return table
