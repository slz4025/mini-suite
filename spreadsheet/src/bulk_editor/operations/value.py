from flask import render_template

import src.command_palette as command_palette
import src.errors.types as err_types
import src.selector.types as sel_types
import src.utils.form as form_helpers

import src.bulk_editor.modifications as modifications
from src.bulk_editor.operations.operation import Operation
import src.bulk_editor.operations.selection as selection


class Value(Operation):
    @classmethod
    def name(cls):
        return "Value"

    @classmethod
    def icon(cls):
        return ""

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
                    f"Value operation does not support selection type {sel_type}."
                )
        else:
            raise err_types.NotSupportedError(f"Value does not accept a selection of purpose {use}.")

        return sel

    @classmethod
    def apply(cls, form):
        sel = selection.get(cls.name(), "input")
        sel_types.check_selection(sel)

        value = form_helpers.extract(form, "value", name="value")
        if value == "":
            raise err_types.InputError("Field 'value' was not given.")

        modifications.apply_transaction(
            modifications.Transaction(
                modification_name="VALUE",
                input=modifications.ValueInput(selection=sel, value=value),
            )
        )

    @classmethod
    def render(cls):
        show_help = command_palette.state.get_show_help()
        use_sel = selection.render(cls.name(), "input")
        return render_template(
                "partials/bulk_editor/value.html",
                show_help=show_help,
                use_sel=use_sel,
                value="",
        )
