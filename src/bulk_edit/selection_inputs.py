import re

from src.errors import UserError
from src.form import extract, parse_int, validate_bounds, validate_nonempty
from src.sheet import (
    Axis,
    Range,
    CellSelection,
    BoxSelection,
    RangeSelection,
    IndexSelection,
    IndicesSelection,
    get_bounds,
    get_all_indices,
    set_range,
)
from src.types import Index


range_pattern = "^([0-9]*)(:[0-9]*)?$"
range_re = re.compile(range_pattern)


def validate_range(axis, r):
    start, end = set_range(axis, r)

    bounds = get_bounds()
    match axis:
        case Axis.ROW:
            bound = bounds.row
            name = "Row"
        case Axis.COLUMN:
            bound = bounds.col
            name = "Column"

    validate_bounds(start, 0, bound, name="start")
    validate_bounds(end, 0, bound, name="end")

    if end <= start:
        raise UserError(
            f"{name} end, {end}, is not greater than start, {start}."
        )


def ranges(query):
    entries = query.split(",")
    entries = [e.strip() for e in entries]
    entries = [e for e in entries if e != ""]
    rs = []
    for e in entries:
        m = range_re.search(e)
        if not m:
            raise UserError(
                f"Pattern '{e}' does not match a valid index or range."
            )
        else:
            raw = m.groups()[0]
            first = None
            second = None
            if raw != "":
                first = parse_int(raw, "start")
                second = first+1

            raw = m.groups()[1]
            if raw is not None:
                raw = raw[1:]
                if raw != "":
                    second = parse_int(raw, "end")
                else:
                    second = None  # handles case like '1:'
            range = Range(first, second)
            rs.append(range)

    if len(rs) == 0:
        rs.append(Range(None, None))

    return rs


def row_range(form):
    start = extract(form, "selection-start", name="start")
    start = None if start == "" else parse_int(start, name="start")
    end = extract(form, "selection-end", name="end")
    end = None if end == "" else parse_int(end, name="end")
    r = Range(start=start, end=end)
    validate_range(axis=Axis.ROW, r=r)
    sel = RangeSelection(axis=Axis.ROW, range=r)
    return sel


def col_range(form):
    start = extract(form, "selection-start", name="start")
    start = None if start == "" else parse_int(start, name="start")
    end = extract(form, "selection-end", name="end")
    end = None if end == "" else parse_int(end, name="end")
    r = Range(start=start, end=end)
    validate_range(axis=Axis.COLUMN, r=r)
    sel = RangeSelection(axis=Axis.COLUMN, range=r)
    return sel


def row_index(form):
    index = extract(form, "selection-index", name="index")
    validate_nonempty(index, name="index")
    index = parse_int(index, name="index")
    validate_bounds(index, 0, get_bounds().row, name="index")
    return IndexSelection(axis=Axis.ROW, index=index)


def col_index(form):
    index = extract(form, "selection-index", name="index")
    validate_nonempty(index, name="index")
    index = parse_int(index, name="index")
    validate_bounds(index, 0, get_bounds().col, name="index")
    return IndexSelection(axis=Axis.COLUMN, index=index)


def row_indices(form):
    query = extract(form, "selection-query", name="query")
    rs = ranges(query)
    for r in rs:
        validate_range(axis=Axis.ROW, r=r)
    indices = get_all_indices(axis=Axis.ROW, ranges=rs)
    sel = IndicesSelection(axis=Axis.ROW, indices=indices)
    return sel


def col_indices(form):
    query = extract(form, "selection-query", name="query")
    rs = ranges(query)
    for r in rs:
        validate_range(axis=Axis.COLUMN, r=r)
    indices = get_all_indices(axis=Axis.COLUMN, ranges=rs)
    sel = IndicesSelection(axis=Axis.COLUMN, indices=indices)
    return sel


def cell(form):
    row = extract(form, "selection-row", name="row")
    validate_nonempty(row, name="row")
    row = parse_int(row, name="row")
    validate_bounds(row, 0, get_bounds().row, name="row")

    col = extract(form, "selection-col", name="column")
    validate_nonempty(col, name="column")
    col = parse_int(col, name="column")
    validate_bounds(col, 0, get_bounds().col, name="column")

    sel = CellSelection(index=Index(row=row, col=col))
    return sel


def box(form):
    sr = extract(form, "selection-sr", name="starting row")
    sr = None if sr == "" else parse_int(sr, name="starting row")
    er = extract(form, "selection-er", name="ending row")
    er = None if er == "" else parse_int(er, name="ending row")
    sc = extract(form, "selection-sc", name="starting column")
    sc = None if sc == "" else parse_int(sc, name="starting column")
    ec = extract(form, "selection-ec", name="ending column")
    ec = None if ec == "" else parse_int(ec, name="ending column")

    row_range = Range(start=sr, end=er)
    validate_range(axis=Axis.ROW, r=row_range)
    col_range = Range(start=sc, end=ec)
    validate_range(axis=Axis.COLUMN, r=col_range)

    sel = BoxSelection(rows=row_range, cols=col_range)
    return sel