from src.form import extract, parse_int, validate_nonempty

import src.data.selections as selections
import src.data.sheet as sheet


def get_row_index(form):
    name = "row index"
    index = extract(form, "selection-row-index", name=name)
    validate_nonempty(index, name=name)
    index = parse_int(index, name=name)

    return selections.RowIndex(index)


def get_col_index(form):
    name = "column index"
    index = extract(form, "selection-col-index", name=name)
    validate_nonempty(index, name=name)
    index = parse_int(index, name=name)

    return selections.ColIndex(index)


def get_cell_position(form):
    row_index = get_row_index(form)
    col_index = get_col_index(form)

    sel = selections.CellPosition(row_index=row_index, col_index=col_index)
    return sel


def get_row_range(form):
    name = "row start"
    start = extract(form, "selection-row-start", name=name)
    start = None if start == "" else sheet.Index(parse_int(start, name=name))

    name = "row end"
    end = extract(form, "selection-row-end", name=name)
    end = None if end == "" else sheet.Bound(parse_int(end, name=name))

    sel = selections.RowRange(start=start, end=end)
    return sel


def get_col_range(form):
    name = "column start"
    start = extract(form, "selection-col-start", name=name)
    start = None if start == "" else sheet.Index(parse_int(start, name=name))

    name = "column end"
    end = extract(form, "selection-col-end", name=name)
    end = None if end == "" else sheet.Bound(parse_int(end, name=name))

    sel = selections.ColRange(start=start, end=end)
    return sel


def get_box(form):
    row_range = get_row_range(form)
    col_range = get_col_range(form)

    sel = selections.Box(row_range=row_range, col_range=col_range)
    return sel
