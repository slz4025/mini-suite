from flask import render_template

import src.command_palette as command_palette
import src.sheet.types as sheet_types
import src.utils.form as form_helpers

from src.selector.selector import Selector
import src.selector.checkers as checkers
import src.selector.state as state
import src.selector.types as types


class Columns(Selector):
    @classmethod
    def name(cls):
        return "Columns"

    @classmethod
    def validate_and_parse(cls, form):
        name = "column start"
        start = form_helpers.extract(form, "col-start", name=name)
        start = None if start == "" else sheet_types.Index(
            form_helpers.parse_int(start, name=name)
        )

        name = "column end"
        end = form_helpers.extract(form, "col-end", name=name)
        end = None if end == "" else sheet_types.Bound(
            # make exclusive
            form_helpers.parse_int(end, name=name)+1
        )

        sel = types.ColRange(start=start, end=end)
        sel = checkers.check_and_set_col_range(sel)
        return sel

    @classmethod
    def render(cls):
        show_help = command_palette.state.get_show_help()
        selection = state.get_selection()

        col_start = None
        col_end = None
        if isinstance(selection, types.ColRange):
            col_start = selection.start.value
            # make inclusive
            col_end = selection.end.value-1

        return render_template(
            "partials/selector/col_range.html",
            show_help=show_help,
            col_start=col_start,
            col_end=col_end,
        )
