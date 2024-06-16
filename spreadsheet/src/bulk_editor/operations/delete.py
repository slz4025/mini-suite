from flask import render_template

import src.errors.types as err_types
import src.selector.modes as sel_modes
import src.selector.types as sel_types

import src.bulk_editor.modifications as modifications
from src.bulk_editor.operations.operation import Operation
import src.bulk_editor.operations.selection as selection


class Delete(Operation):
    @classmethod
    def name(cls):
        return "Delete"

    @classmethod
    def icon(cls):
        return "❌"

    @classmethod
    def validate_selection(cls, use, sel):
        if use == "input":
            sel_mode = sel_modes.from_selection(sel)
            selection_mode_options = [
                sel_types.Mode.ROWS,
                sel_types.Mode.COLUMNS,
            ]
            if sel_mode not in selection_mode_options:
                raise err_types.NotSupportedError(
                    f"Delete operation does not support selection mode {sel_mode.value}."
                )
        else:
            raise err_types.NotSupportedError(f"Delete does not accept a selection of purpose {use}.")

        return sel

    @classmethod
    def validate_and_parse(cls, form):
        sel = selection.get(cls.name(), "input")
        sel_types.check_selection(sel)

        modification = modifications.Transaction(
            modification_name="DELETE",
            input=modifications.DeleteInput(selection=sel),
        )
        return [modification]

    @classmethod
    def apply(cls, mods):
        for modification in mods:
            modifications.apply_transaction(modification)

    @classmethod
    def render(cls):
        use_sel = selection.render(cls.name(), "input")
        return render_template(
                "partials/bulk_editor/delete.html",
                use_sel=use_sel,
        )
