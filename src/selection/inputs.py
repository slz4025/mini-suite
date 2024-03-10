from dataclasses import dataclass
from typing import Callable

import src.form_helpers as form_helpers

import src.errors as errors
import src.selection.types as types
import src.data.sheet as sheet


def get_row_index(inp):
    name = "row index"
    index = form_helpers.extract(inp, "row-index", name=name)
    form_helpers.validate_nonempty(index, name=name)
    index = form_helpers.parse_int(index, name=name)

    sel = types.RowIndex(index)
    types.check_row_index(sel)
    return sel


def get_col_index(inp):
    name = "column index"
    index = form_helpers.extract(inp, "col-index", name=name)
    form_helpers.validate_nonempty(index, name=name)
    index = form_helpers.parse_int(index, name=name)

    sel = types.ColIndex(index)
    types.check_col_index(sel)
    return sel


def get_cell_position(inp):
    row_index = get_row_index(inp)
    col_index = get_col_index(inp)

    sel = types.CellPosition(row_index=row_index, col_index=col_index)
    types.check_cell_position(sel)
    return sel


def get_row_range(inp):
    name = "row start"
    start = form_helpers.extract(inp, "row-start", name=name)
    start = None if start == "" else sheet.Index(
        form_helpers.parse_int(start, name=name)
    )

    name = "row end"
    end = form_helpers.extract(inp, "row-end", name=name)
    end = None if end == "" else sheet.Bound(
        form_helpers.parse_int(end, name=name)
    )

    sel = types.RowRange(start=start, end=end)
    sel = types.check_and_set_row_range(sel)
    return sel


def get_col_range(inp):
    name = "column start"
    start = form_helpers.extract(inp, "col-start", name=name)
    start = None if start == "" else sheet.Index(
        form_helpers.parse_int(start, name=name)
    )

    name = "column end"
    end = form_helpers.extract(inp, "col-end", name=name)
    end = None if end == "" else sheet.Bound(
        form_helpers.parse_int(end, name=name)
    )

    sel = types.ColRange(start=start, end=end)
    sel = types.check_and_set_col_range(sel)
    return sel


def get_box(inp):
    row_range = get_row_range(inp)
    col_range = get_col_range(inp)

    sel = types.Box(row_range=row_range, col_range=col_range)
    sel = types.check_and_set_box(sel)
    return sel


@dataclass
class Form:
    name: str
    template: str
    validate_and_parse: Callable[[object], types.Selection]


forms = {
    "Rows": Form(
        name="Rows",
        template="row_range.html",
        validate_and_parse=get_row_range,
    ),
    "Columns": Form(
        name="Columns",
        template="col_range.html",
        validate_and_parse=get_col_range,
    ),
    "Box": Form(
        name="Box",
        template="box.html",
        validate_and_parse=get_box,
    ),
    "Row": Form(
        name="Row",
        template="row_index.html",
        validate_and_parse=get_row_index,
    ),
    "Column": Form(
        name="Column",
        template="col_index.html",
        validate_and_parse=get_col_index,
    ),
    "Cell Position": Form(
        name="Cell Position",
        template="cell_position.html",
        validate_and_parse=get_cell_position,
    ),
}
options = list(forms.keys())


def mode_from_selection(sel):
    if isinstance(sel, types.RowIndex):
        return "Row"
    elif isinstance(sel, types.ColIndex):
        return "Column"
    elif isinstance(sel, types.CellPosition):
        return "Cell Position"
    elif isinstance(sel, types.RowRange):
        return "Rows"
    elif isinstance(sel, types.ColRange):
        return "Columns"
    elif isinstance(sel, types.Box):
        return "Box"
    else:
        sel_type = type(sel)
        raise errors.UnknownOptionError(
            f"Unknown selection type: {sel_type}."
        )


def get_form(mode):
    if mode in forms:
        return forms[mode]
    else:
        raise errors.UnknownOptionError(
            f"Unknown selection mode: {mode}."
        )


def validate_and_parse(inp):
    mode = form_helpers.extract(inp, "mode", name="selection mode")
    form = get_form(mode)
    selection = form.validate_and_parse(inp)
    return selection
