from flask import render_template

import src.command_palette as command_palette

from src.selector.row import Row
from src.selector.column import Column
from src.selector.selector import Selector
import src.selector.state as state
import src.selector.types as types


class CellPosition(Selector):
    @classmethod
    def name(cls):
        return "Cell Position"

    @classmethod
    def validate_and_parse(cls, form):
        row_index = Row.validate_and_parse(form)
        col_index = Column.validate_and_parse(form)

        sel = types.CellPosition(row_index=row_index, col_index=col_index)
        types.check_cell_position(sel)
        return sel

    @classmethod
    def render(cls):
        show_help = command_palette.state.get_show_help()
        selection = state.get_selection()

        row_index = None
        col_index = None
        if isinstance(selection, types.CellPosition):
            row_index = selection.row_index.value
            col_index = selection.col_index.value

        return render_template(
            "partials/selector/cell_position.html",
            show_help=show_help,
            row_index=row_index,
            col_index=col_index,
        )
