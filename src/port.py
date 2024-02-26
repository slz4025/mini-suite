from flask import render_template

from src.errors import ClientError, UserError
from src.form import extract, parse_int, validate_bounds
from src.settings import get_settings
from src.sheet import get_value, get_bounds, check_index
from src.types import Index


def cells_equal(cell1, cell2):
    return cell1.row == cell2.row and cell1.col == cell2.col


def get_focused_cell(session):
    return Index(
        row=int(session["focused-cell"]["row"]),
        col=int(session["focused-cell"]["col"]),
    )


def set_focused_cell(session, focused_cell):
    session["focused-cell"] = {
        "row": str(focused_cell.row),
        "col": str(focused_cell.col),
    }


def is_focused(session, cell):
    focused_cell = get_focused_cell(session)
    return cells_equal(focused_cell, cell)


def get_upperleft(session):
    return Index(
        row=int(session["upper-left"]["row"]),
        col=int(session["upper-left"]["col"]),
    )


def set_upperleft(session, upperleft):
    session["upper-left"] = {
        "row": str(upperleft.row),
        "col": str(upperleft.col),
    }


def set_center(session, form):
    maxindex = get_bounds()

    settings = get_settings(session)
    nrows = settings.nrows
    ncols = settings.ncols

    row = extract(form, "center-cell-row", name="row")
    row = parse_int(row, name="row")
    validate_bounds(row, 0, maxindex.row, "row")

    col = extract(form, "center-cell-col", name="col")
    col = parse_int(col, name="col")
    validate_bounds(col, 0, maxindex.col, "column")

    bound = maxindex.row
    if row >= bound:
        raise UserError(f"Row index, {row}, is not within bounds, {bound}.")
    bound = maxindex.col
    if col >= bound:
        raise UserError(f"Row index, {col}, is not within bounds, {bound}.")

    row_end = min(row + (nrows) // 2 + 1, maxindex.row)
    col_end = min(col + (ncols) // 2 + 1, maxindex.col)
    row_start = max(0, row_end - nrows)
    col_start = max(0, col_end - ncols)

    upperleft = Index(row=row_start, col=col_start)
    set_upperleft(session, upperleft)


def move_upperleft(session, method):
    upperleft = get_upperleft(session)

    settings = get_settings(session)
    mrows = settings.mrows
    mcols = settings.mcols

    maxindex = get_bounds()

    if method == 'home':
        moved = Index(row=0, col=0)
    else:
        match method:
            case 'up':
                delta = Index(row=-mrows, col=0)
            case 'down':
                delta = Index(row=mrows, col=0)
            case 'left':
                delta = Index(row=0, col=-mcols)
            case 'right':
                delta = Index(row=0, col=mcols)
            case _:
                raise ClientError(f"Unexpected method: {method}.")

        row = upperleft.row
        potential_row = max(0, upperleft.row+delta.row)
        if potential_row < maxindex.row:
            row = potential_row

        col = upperleft.col
        potential_col = max(0, upperleft.col+delta.col)
        if potential_col < maxindex.col:
            col = potential_col

        moved = Index(row=row, col=col)

    set_upperleft(session, moved)


def init_port(session):
    upperleft = Index(row=0, col=0)
    set_upperleft(session, upperleft)
    focused_cell = Index(row=0, col=0)
    set_focused_cell(session, focused_cell)


def render_cell(session, index, highlight=False):
    check_index(index)

    show_highlight = highlight and is_focused(session, index)

    value = get_value(index.row, index.col)
    if value is None:
        value = ""
    return render_template(
            "partials/port/cell.html",
            row=index.row,
            col=index.col,
            data=value,
            show_highlight=show_highlight,
    )


def render_header(session, axis, index):
    return render_template(
        "partials/port/header.html",
        axis=axis,
        index=index,
        data=index,
    )


def render_row(session, leftmost, ncols, maxindex):
    row = leftmost.row

    header = render_header(session, axis="row", index=row)

    cells = []
    for col in range(leftmost.col, min(leftmost.col+ncols, maxindex.col)):
        cell = render_cell(session, Index(row=row, col=col))
        cells.append(cell)

    return render_template(
            "partials/port/row.html",
            header=header,
            data="\n".join(cells),
    )


def render_table_header(session, upperleft, ncols, maxindex):
    corner = render_header(session, axis="none", index="")

    header = []
    for col in range(upperleft.col, min(upperleft.col+ncols, maxindex.col)):
        h = render_header(session, axis="col", index=col)
        header.append(h)

    return render_template(
            "partials/port/row.html",
            header=corner,
            data="\n".join(header),
    )


def render_table(session, upperleft, nrows, ncols, maxindex):
    header = render_table_header(session, upperleft, ncols, maxindex)

    tablerows = []
    col = upperleft.col
    for row in range(upperleft.row, min(upperleft.row+nrows, maxindex.row)):
        tablerow = render_row(
            session,
            Index(row=row, col=col),
            ncols,
            maxindex,
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
    maxindex = get_bounds()
    table = render_table(
        session,
        upperleft=upperleft,
        nrows=settings.nrows,
        ncols=settings.ncols,
        maxindex=maxindex,
    )
    return table
