from dataclasses import dataclass
from flask import render_template
import os
from typing import Callable

import src.command_palette as command_palette
import src.errors.types as err_types
import src.utils.form as form_helpers

import src.selector.modes as modes
import src.selector.types as types
import src.sheet.types as sheet_types


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
    start = None if start == "" else sheet_types.Index(
        form_helpers.parse_int(start, name=name)
    )

    name = "row end"
    end = form_helpers.extract(inp, "row-end", name=name)
    end = None if end == "" else sheet_types.Bound(
        # make exclusive
        form_helpers.parse_int(end, name=name)+1
    )

    sel = types.RowRange(start=start, end=end)
    sel = types.check_and_set_row_range(sel)
    return sel


def get_col_range(inp):
    name = "column start"
    start = form_helpers.extract(inp, "col-start", name=name)
    start = None if start == "" else sheet_types.Index(
        form_helpers.parse_int(start, name=name)
    )

    name = "column end"
    end = form_helpers.extract(inp, "col-end", name=name)
    end = None if end == "" else sheet_types.Bound(
        # make exclusive
        form_helpers.parse_int(end, name=name)+1
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
    mode: types.Mode
    template: str
    validate_and_parse: Callable[[object], types.Selection]


forms = {
    types.Mode.ROWS: Form(
        mode=types.Mode.ROWS,
        template="row_range.html",
        validate_and_parse=get_row_range,
    ),
    types.Mode.COLUMNS: Form(
        mode=types.Mode.COLUMNS,
        template="col_range.html",
        validate_and_parse=get_col_range,
    ),
    types.Mode.BOX: Form(
        mode=types.Mode.BOX,
        template="box.html",
        validate_and_parse=get_box,
    ),
    types.Mode.ROW_INDEX: Form(
        mode=types.Mode.ROW_INDEX,
        template="row_index.html",
        validate_and_parse=get_row_index,
    ),
    types.Mode.COLUMN_INDEX: Form(
        mode=types.Mode.COLUMN_INDEX,
        template="col_index.html",
        validate_and_parse=get_col_index,
    ),
    types.Mode.CELL_POSITION: Form(
        mode=types.Mode.CELL_POSITION,
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


def render(mode, sel=None):
    show_help = command_palette.state.get_show_help()

    row_index = ""
    col_index = ""
    row_start = ""
    row_end = ""
    col_start = ""
    col_end = ""

    if sel is not None:
        if isinstance(sel, types.RowIndex):
            row_index = sel.value
        elif isinstance(sel, types.ColIndex):
            col_index = sel.value
        elif isinstance(sel, types.CellPosition):
            row_index = sel.row_index.value
            col_index = sel.col_index.value
        elif isinstance(sel, types.RowRange):
            row_start = sel.start.value
            # make inclusive
            row_end = sel.end.value - 1
        elif isinstance(sel, types.ColRange):
            col_start = sel.start.value
            # make inclusive
            col_end = sel.end.value - 1
        elif isinstance(sel, types.Box):
            row_start = sel.row_range.start.value
            # make inclusive
            row_end = sel.row_range.end.value - 1
            col_start = sel.col_range.start.value
            # make inclusive
            col_end = sel.col_range.end.value - 1
        else:
            sel_type = type(sel)
            raise err_types.UnknownOptionError(
                f"Unknown selection type: {sel_type}."
            )

    form = forms[mode]

    template_path = os.path.join(
        "partials/selector",
        form.template,
    )
    html = render_template(
        template_path,
        show_help=show_help,
        row_index=row_index,
        col_index=col_index,
        row_start=row_start,
        row_end=row_end,
        col_start=col_start,
        col_end=col_end,
    )
    return html
