from flask import render_template

import src.command_palette as command_palette
import src.sheet.types as sheet_types
import src.utils.form as form_helpers

from src.selector.selector import Selector
import src.selector.state as state
import src.selector.types as types


class Rows(Selector):
    @classmethod
    def name(cls):
        return "Rows"

    @classmethod
    def validate_and_parse(cls, form):
        name = "row start"
        start = form_helpers.extract(form, "row-start", name=name)
        start = None if start == "" else sheet_types.Index(
            form_helpers.parse_int(start, name=name)
        )

        name = "row end"
        end = form_helpers.extract(form, "row-end", name=name)
        end = None if end == "" else sheet_types.Bound(
            # make exclusive
            form_helpers.parse_int(end, name=name)+1
        )

        sel = types.RowRange(start=start, end=end)
        sel = types.check_and_set_row_range(sel)
        return sel

    @classmethod
    def render(cls):
        show_help = command_palette.state.get_show_help()
        selection = state.get_selection()

        row_start = None
        row_end = None
        if isinstance(selection, types.RowRange):
            row_start = selection.start.value
            # make inclusive
            row_end = selection.end.value - 1

        return render_template(
            "partials/selector/row_range.html",
            show_help=show_help,
            row_start=row_start,
            row_end=row_end,
        )
