from flask import render_template

import src.sheet as sheet
import src.editor as editor
import src.errors.types as err_types
import src.selector.checkers as sel_checkers
import src.selector.helpers as sel_helpers
import src.selector.state as sel_state
import src.selector.types as sel_types


def make_render_selected():
    sel = sel_state.get_selection()

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
            sel_helpers.get_bounds_from_selection(sel)

        def render_selected(cp): return "selected-current" \
            if cp.in_bounds(start_row, end_row, start_col, end_col) else ""
    elif isinstance(sel, sel_types.ColRange):
        start_row, end_row, start_col, end_col = \
            sel_helpers.get_bounds_from_selection(sel)

        def render_selected(cp): return "selected-current" \
            if cp.in_bounds(start_row, end_row, start_col, end_col) else ""
    elif isinstance(sel, sel_types.Box):
        start_row, end_row, start_col, end_col = \
            sel_helpers.get_bounds_from_selection(sel)

        def render_selected(cp): return "selected-current" \
            if cp.in_bounds(start_row, end_row, start_col, end_col) else ""
    else:
        def render_selected(cp): return ""

    return render_selected


def render_cell(
    cell_position,
    render_selected=None,
    catch_failure=False,
):
    sel_checkers.check_cell_position(cell_position)

    editing = editor.is_editing(cell_position)
    markdown = sheet.is_markdown(cell_position)

    renders = []
    input_render = None

    # Apply in reverse order of precendence.
    if markdown:
        renders.append("markdown")

    if render_selected is None:
        render_selected = make_render_selected()
    render_selected_state = render_selected(cell_position)
    if "selected-current" in render_selected_state:
        input_render = "selected"
    renders.append(render_selected_state)

    if editing:
        renders.append("editing-current")
        input_render = "editing"

    if editing:
        # trigger error on rendering for edit if computation is invalid
        if not catch_failure:
            try:
                sheet.get_cell_computed(
                    cell_position,
                )
            except err_types.UserError as e:
                raise e
        value = sheet.data.get_cell_value(cell_position)
    else:
        try:
            value = sheet.get_cell_computed(
                cell_position,
            )
        except err_types.UserError as e:
            if catch_failure:
                # set as empty while report error
                value = ""
                renders.append("failure")
            else:
                raise e

    if value is None:
        value = ""

    row = cell_position.row_index.value
    col = cell_position.col_index.value

    return render_template(
            "partials/port/cell.html",
            row=row,
            col=col,
            editing=editing,
            markdown=markdown,
            data=value,
            renders=renders,
            input_render=input_render if input_render is not None else '',
    )


def render_corner_header(render_selected=None):
    cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(-1),
        col_index=sel_types.ColIndex(-1),
    )

    renders = []
    if render_selected is None:
        render_selected = make_render_selected()
    render_selected_state = render_selected(cell_position)
    renders.append(render_selected_state)

    return render_template(
        "partials/port/corner_header.html",
        data="",
        renders=renders,
    )


def render_row_header(row_index, render_selected=None):
    cell_position = sel_types.CellPosition(
        row_index=row_index,
        col_index=sel_types.ColIndex(-1),
    )

    renders = []
    if render_selected is None:
        render_selected = make_render_selected()
    render_selected_state = render_selected(cell_position)
    renders.append(render_selected_state)

    return render_template(
        "partials/port/row_header.html",
        index=row_index.value,
        data=row_index.value,
        renders=renders,
    )


def render_col_header(col_index, render_selected=None):
    cell_position = sel_types.CellPosition(
        row_index=sel_types.RowIndex(-1),
        col_index=col_index,
    )

    renders = []
    if render_selected is None:
        render_selected = make_render_selected()
    render_selected_state = render_selected(cell_position)
    renders.append(render_selected_state)

    return render_template(
        "partials/port/col_header.html",
        index=col_index.value,
        data=col_index.value,
        renders=renders,
    )


def render_row(
    leftmost,
    ncols,
    bounds,
    render_selected,
    min_height="100",
    catch_failure=False,
):
    header = render_row_header(
        leftmost.row_index,
        render_selected=render_selected,
    )

    row = [header]
    for col in range(
        leftmost.col_index.value,
        min(leftmost.col_index.value+ncols, bounds.col.value)
    ):
        cell = render_cell(
            sel_types.CellPosition(
                row_index=leftmost.row_index,
                col_index=sel_types.ColIndex(col),
            ),
            render_selected=render_selected,
            catch_failure=catch_failure,
        )
        row.append(cell)

    return row


def render_header(
    upperleft,
    ncols,
    bounds,
    render_selected,
):
    corner = render_corner_header(render_selected=render_selected)

    row = [corner]
    for col in range(
        upperleft.col_index.value,
        min(upperleft.col_index.value+ncols, bounds.col.value)
    ):
        header = render_col_header(
            sel_types.ColIndex(col),
            render_selected=render_selected,
        )
        row.append(header)

    return row


def render_table(
    upperleft,
    nrows,
    ncols,
    bounds,
    catch_failure=False,
):
    render_selected = make_render_selected()

    header = render_header(
        upperleft,
        ncols,
        bounds,
        render_selected,
    )

    gridrows = []
    for row in range(
        upperleft.row_index.value,
        min(upperleft.row_index.value+nrows, bounds.row.value)
    ):
        gridrow = render_row(
            sel_types.CellPosition(
                row_index=sel_types.RowIndex(row),
                col_index=upperleft.col_index,
            ),
            ncols,
            bounds,
            render_selected,
            min_height=100.0 / float(nrows + 1),
            catch_failure=catch_failure,
        )
        gridrows.append(gridrow)

    grid = [header] + gridrows
    data = "\n".join(["\n".join(row) for row in grid])
    return render_template(
            "partials/port/grid.html",
            data=data,
            num_rows=len(grid),
            num_cols=len(header),
    )
