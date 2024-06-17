from flask import render_template

import src.command_palette as command_palette

from src.selector.selector import Selector
from src.selector.rows import Rows
from src.selector.columns import Columns
import src.selector.state as state
import src.selector.types as types


class Box(Selector):
    @classmethod
    def name(cls):
        return "Box"

    @classmethod
    def validate_and_parse(cls, form):
        row_range = Rows.validate_and_parse(form)
        col_range = Columns.validate_and_parse(form)

        selection = types.Box(row_range=row_range, col_range=col_range)
        selection = types.check_and_set_box(selection)
        return selection

    @classmethod
    def render(cls):
        show_help = command_palette.state.get_show_help()
        selection = state.get_selection()

        row_start = None
        row_end = None
        col_start = None
        col_end = None
        if isinstance(selection, types.Box):
            row_start = selection.row_range.start.value
            # make inclusive
            row_end = selection.row_range.end.value-1
            col_start = selection.col_range.start.value
            # make inclusive
            col_end = selection.col_range.end.value-1

        return render_template(
            "partials/selector/box.html",
            show_help=show_help,
            row_start=row_start,
            row_end=row_end,
            col_start=col_start,
            col_end=col_end,
        )
