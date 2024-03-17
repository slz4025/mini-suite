from dataclasses import dataclass
from typing import Callable

import src.form_helpers as form_helpers

import src.selection.modes as modes
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
    mode: modes.Mode
    template: str
    validate_and_parse: Callable[[object], types.Selection]


forms = {
    modes.Mode.ROWS: Form(
        mode=modes.Mode.ROWS,
        template="row_range.html",
        validate_and_parse=get_row_range,
    ),
    modes.Mode.COLUMNS: Form(
        mode=modes.Mode.COLUMNS,
        template="col_range.html",
        validate_and_parse=get_col_range,
    ),
    modes.Mode.BOX: Form(
        mode=modes.Mode.BOX,
        template="box.html",
        validate_and_parse=get_box,
    ),
    modes.Mode.ROW: Form(
        mode=modes.Mode.ROW,
        template="row_index.html",
        validate_and_parse=get_row_index,
    ),
    modes.Mode.COLUMN: Form(
        mode=modes.Mode.COLUMN,
        template="col_index.html",
        validate_and_parse=get_col_index,
    ),
    modes.Mode.CELL_POSITION: Form(
        mode=modes.Mode.CELL_POSITION,
        template="cell_position.html",
        validate_and_parse=get_cell_position,
    ),
}
options = list(forms.keys())


def validate_and_parse(inp):
    mode_str = form_helpers.extract(inp, "mode", name="selection mode")
    mode = modes.from_input(mode_str)
    form = forms[mode]
    selection = form.validate_and_parse(inp)
    return selection
