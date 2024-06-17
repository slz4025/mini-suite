from flask import render_template

import src.errors.types as err_types
import src.selector.types as sel_types

import src.bulk_editor.modifications as modifications
from src.bulk_editor.operations.operation import Operation
import src.bulk_editor.operations.selection as selection


class Erase(Operation):
    @classmethod
    def name(cls):
        return "Erase"

    @classmethod
    def icon(cls):
        return "🗑"

    @classmethod
    def validate_selection(cls, use, sel):
        if use == "input":
            sel_type = type(sel)
            selection_type_options = [
                sel_types.RowRange,
                sel_types.ColRange,
                sel_types.Box,
            ]
            if sel_type not in selection_type_options:
                raise err_types.NotSupportedError(
                    f"Erase operation does not support selection type {sel_type}."
                )
        else:
            raise err_types.NotSupportedError(f"Erase does not accept a selection of purpose {use}.")

        return sel

    @classmethod
    def apply(cls, form):
        sel = selection.get(cls.name(), "input")
        sel_types.check_selection(sel)

        modifications.apply_transaction(
            modifications.Transaction(
                modification_name="VALUE",
                input=modifications.ValueInput(selection=sel, value=None),
            )
        )

    @classmethod
    def render(cls):
        use_sel = selection.render(cls.name(), "input")
        return render_template(
                "partials/bulk_editor/erase.html",
                use_sel=use_sel,
        )
