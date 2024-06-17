from flask import render_template

import src.command_palette as command_palette
import src.utils.form as form_helpers

from src.selector.selector import Selector
import src.selector.state as state
import src.selector.types as types


class Column(Selector):
    @classmethod
    def name(cls):
        return "Column"

    @classmethod
    def validate_and_parse(cls, form):
        name = "column index"
        index = form_helpers.extract(form, "col-index", name=name)
        form_helpers.validate_nonempty(index, name=name)
        index = form_helpers.parse_int(index, name=name)

        sel = types.ColIndex(index)
        types.check_col_index(sel)
        return sel

    @classmethod
    def render(cls):
        show_help = command_palette.state.get_show_help()
        selection = state.get_selection()

        col_index = None
        if isinstance(selection, types.ColIndex):
            col_index = selection.value

        return render_template(
            "partials/selector/col_index.html",
            show_help=show_help,
            col_index=col_index,
        )
