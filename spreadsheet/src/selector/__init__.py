from flask import render_template

import src.command_palette as command_palette
import src.errors.types as err_types
import src.utils.form as form_helpers

import src.selector.helpers as helpers
import src.selector.search as search
import src.selector.state as state
import src.selector.types as types

from src.selector.row import Row
from src.selector.column import Column
from src.selector.cell_position import CellPosition
from src.selector.rows import Rows
from src.selector.columns import Columns
from src.selector.box import Box

selectors = [
    Row,
    Column,
    CellPosition,
    Rows,
    Columns,
    Box,
]
selectors_map = {s.name(): s for s in selectors}


def validate_and_parse(form):
    name = form_helpers.extract(form, "name", name="selection name")
    selector = selectors_map[name]
    selection = selector.validate_and_parse(form)
    return selection


def render_input(name):
    selector = selectors_map[name]
    return selector.render()


def compute_from_endpoints(start, end):
    sel = helpers.compute_from_endpoints(start, end)
    return sel


def compute_updated_selection(direction):
    sel = state.get_selection()
    updated_sel = helpers.compute_updated_selection(sel, direction)
    return updated_sel


def render(name=None):
    show_help = command_palette.state.get_show_help()
    show_selector = command_palette.state.get_show_selector()

    options = [o for o in selectors_map.keys()]
    selection = state.get_selection()

    if name is None:
        if selection is not None:
            if isinstance(selection, types.RowIndex):
                name = "Row"
            elif isinstance(selection, types.ColIndex):
                name = "Column"
            elif isinstance(selection, types.CellPosition):
                name = "Cell Position"
            elif isinstance(selection, types.RowRange):
                name = "Rows"
            elif isinstance(selection, types.ColRange):
                name = "Columns"
            elif isinstance(selection, types.Box):
                name = "Box"
            else:
                sel_type = type(selection)
                raise err_types.UnknownOptionError(
                    f"Unknown selection type: {sel_type}."
                )
        else:
            name = options[0]

    sel_type = type(selection)
    show_adjustments = sel_type in [
        types.Box,
        types.RowRange,
        types.ColRange,
    ]
    show_row_adjustments = sel_type in [
        types.Box,
        types.RowRange,
    ]
    show_col_adjustments = sel_type in [
        types.Box,
        types.ColRange,
    ]

    show_search = sel_type == types.CellPosition
    search_html = search.render()

    inp = render_input(name)

    return render_template(
            "partials/selector.html",
            show_help=show_help,
            show_selector=show_selector,
            options=options,
            option=name,
            show_search=show_search,
            search=search_html,
            input=inp,
            show_clear=selection is not None,
            show_adjustments=show_adjustments,
            show_row_adjustments=show_row_adjustments,
            show_col_adjustments=show_col_adjustments,
    )
