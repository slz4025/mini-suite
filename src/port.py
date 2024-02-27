from flask import render_template

from src.errors import UnknownOptionError
from src.form import extract, parse_int
from src.settings import get_settings

import src.data.operations as operations
import src.data.selections as selections
import src.data.sheet as sheet


def cell_position_eq(cell_position, other_cell_position):
    return cell_position.row_index.value \
        == other_cell_position.row_index.value \
        and cell_position.col_index.value \
        == other_cell_position.col_index.value


def get_focused_cell_position(session):
    return selections.CellPosition(
        row_index=selections.RowIndex(
            int(session["focused-cell-position"]["row-index"])
        ),
        col_index=selections.ColIndex(
            int(session["focused-cell-position"]["col-index"])
        ),
    )


def set_focused_cell_position(session, focused_cell_position):
    session["focused-cell-position"] = {
        "row-index": str(focused_cell_position.row_index.value),
        "col-index": str(focused_cell_position.col_index.value),
    }


def is_focused(session, cell_position):
    focused_cell_position = get_focused_cell_position(session)
    return cell_position_eq(focused_cell_position, cell_position)


def get_upperleft(session):
    return selections.CellPosition(
        row_index=selections.RowIndex(int(session["upper-left"]["row-index"])),
        col_index=selections.ColIndex(int(session["upper-left"]["col-index"])),
    )


def set_upperleft(session, upperleft):
    session["upper-left"] = {
        "row-index": str(upperleft.row_index.value),
        "col-index": str(upperleft.col_index.value),
    }


def set_center(session, form):
    settings = get_settings(session)
    nrows = settings.nrows
    ncols = settings.ncols

    row = extract(form, "center-cell-row-index", name="row index")
    row = parse_int(row, name="row index")

    col = extract(form, "center-cell-col-index", name="col index")
    col = parse_int(col, name="column index")

    bounds = sheet.get_bounds()
    row_end = min(row + (nrows) // 2 + 1, bounds.row.value)
    col_end = min(col + (ncols) // 2 + 1, bounds.col.value)
    row_start = max(0, row_end - nrows)
    col_start = max(0, col_end - ncols)

    upperleft = selections.CellPosition(
        row_index=selections.RowIndex(row_start),
        col_index=selections.RowIndex(col_start),
    )
    set_upperleft(session, upperleft)


def move_upperleft(session, method):
    settings = get_settings(session)
    mrows = settings.mrows
    mcols = settings.mcols

    if method == 'home':
        moved = selections.CellPosition(
            row_index=selections.RowIndex(0),
            col_index=selections.ColIndex(0),
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
                raise UnknownOptionError(f"Unexpected method: {method}.")

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

        moved = selections.CellPosition(
            row_index=selections.RowIndex(row),
            col_index=selections.ColIndex(col),
        )

    set_upperleft(session, moved)


def init_port(session):
    upperleft = selections.CellPosition(
        row_index=selections.RowIndex(0),
        col_index=selections.ColIndex(0),
    )
    set_upperleft(session, upperleft)
    focused_cell_position = selections.CellPosition(
        row_index=selections.RowIndex(0),
        col_index=selections.ColIndex(0),
    )
    set_focused_cell_position(session, focused_cell_position)


def render_cell(session, cell_position, highlight=False):
    selections.check_cell_position(cell_position)

    show_highlight = highlight and is_focused(session, cell_position)

    value = operations.get_cell(cell_position)
    if value is None:
        value = ""
    return render_template(
            "partials/port/cell.html",
            row=cell_position.row_index.value,
            col=cell_position.col_index.value,
            data=value,
            show_highlight=show_highlight,
    )


def render_corner_header(session):
    return render_template(
        "partials/port/corner_header.html",
        data="",
    )


def render_row_header(session, row_index):
    return render_template(
        "partials/port/row_header.html",
        index=row_index.value,
        data=row_index.value,
    )


def render_col_header(session, col_index):
    return render_template(
        "partials/port/col_header.html",
        index=col_index.value,
        data=col_index.value,
    )


def render_row(session, leftmost, ncols, bounds):
    header = render_row_header(session, row_index=leftmost.row_index)

    cells = []
    for col in range(
        leftmost.col_index.value,
        min(leftmost.col_index.value+ncols, bounds.col.value)
    ):
        cell = render_cell(
            session,
            selections.CellPosition(
                row_index=leftmost.row_index,
                col_index=selections.ColIndex(col),
            ),
        )
        cells.append(cell)

    return render_template(
            "partials/port/row.html",
            header=header,
            data="\n".join(cells),
    )


def render_table_header(session, upperleft, ncols, bounds):
    corner = render_corner_header(session)

    header = []
    for col in range(
        upperleft.col_index.value,
        min(upperleft.col_index.value+ncols, bounds.col.value)
    ):
        h = render_col_header(session, col_index=selections.ColIndex(col))
        header.append(h)

    return render_template(
            "partials/port/row.html",
            header=corner,
            data="\n".join(header),
    )


def render_table(session, upperleft, nrows, ncols, bounds):
    header = render_table_header(session, upperleft, ncols, bounds)

    tablerows = []
    for row in range(
        upperleft.row_index.value,
        min(upperleft.row_index.value+nrows, bounds.row.value)
    ):
        tablerow = render_row(
            session,
            selections.CellPosition(
                row_index=selections.RowIndex(row),
                col_index=upperleft.col_index,
            ),
            ncols,
            bounds,
        )
        tablerows.append(tablerow)

    return render_template(
            "partials/port/table.html",
            data="\n".join(tablerows),
            header=header,
    )


def render_port(session):
    upperleft = get_upperleft(session)
    settings = get_settings(session)
    bounds = sheet.get_bounds()

    table = render_table(
        session,
        upperleft=upperleft,
        nrows=settings.nrows,
        ncols=settings.ncols,
        bounds=bounds,
    )
    return table
