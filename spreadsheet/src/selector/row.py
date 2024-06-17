from flask import render_template

import src.command_palette as command_palette
import src.utils.form as form_helpers

from src.selector.selector import Selector
import src.selector.state as state
import src.selector.types as types


class Row(Selector):
    @classmethod
    def name(cls):
        return "Row"

    @classmethod
    def validate_and_parse(cls, form):
        name = "row index"
        index = form_helpers.extract(form, "row-index", name=name)
        form_helpers.validate_nonempty(index, name=name)
        index = form_helpers.parse_int(index, name=name)

        sel = types.RowIndex(index)
        types.check_row_index(sel)
        return sel

    @classmethod
    def render(cls):
        show_help = command_palette.state.get_show_help()
        selection = state.get_selection()

        row_index = None
        if isinstance(selection, types.RowIndex):
            row_index = selection.value

        return render_template(
            "partials/selector/row_index.html",
            show_help=show_help,
            row_index=row_index,
        )
