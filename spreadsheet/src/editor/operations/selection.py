from flask import render_template

import src.errors.types as err_types
import src.selector.modes as sel_modes
import src.selector.state as sel_state
import src.selector.types as sel_types

from src.editor.operations.operation import Operation


class Selection(Operation):
    @classmethod
    def name(cls):
        return "selection"

    @classmethod
    def template(cls):
        return "=" + cls._get_selection_macro()

    @classmethod
    def render(cls):
        return render_template(
                "partials/editor/operations/generic.html",
                operation=cls.name(),
                show=cls._show(),
        )

    @classmethod
    def _get_selection_macro(cls):
        sel = sel_state.get_selection()
        if isinstance(sel, sel_types.RowRange):
            macro = "<R#{}:{}>".format(sel.start.value, sel.end.value-1)
        elif isinstance(sel, sel_types.ColRange):
            macro = "<C#{}:{}>".format(sel.start.value, sel.end.value-1)
        elif isinstance(sel, sel_types.Box):
            macro = "<R#{}:{}><C#{}:{}>".format(
                sel.row_range.start.value, sel.row_range.end.value-1,
                sel.col_range.start.value, sel.col_range.end.value-1,
            )
        else:
            sel_mode = sel_modes.from_selection(sel)
            raise err_types.NotSupportedError(
                f"Selection mode {sel_mode.value} is not supported in formulas."
            )
        return macro

    @classmethod
    def _show(cls):
        sel = sel_state.get_selection()
        if isinstance(sel, sel_types.RowRange):
            return True
        elif isinstance(sel, sel_types.ColRange):
            return True
        elif isinstance(sel, sel_types.Box):
            return True
        else:
            return False

