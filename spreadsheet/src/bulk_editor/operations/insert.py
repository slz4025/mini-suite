from flask import render_template

import src.errors.types as err_types
import src.selector.checkers as sel_checkers
import src.selector.types as sel_types
import src.utils.form as form_helpers

import src.bulk_editor.modifications as modifications
from src.bulk_editor.operations.operation import Operation
import src.bulk_editor.operations.selection as selection


class Insert(Operation):
    @classmethod
    def name(cls):
        return "Insert"

    @classmethod
    def icon(cls):
        return "➕"

    @classmethod
    def validate_selection(cls, use, sel):
        if use == "target":
            selection_type_options = [
                sel_types.RowIndex,
                sel_types.ColIndex,
            ]

            sel = selection.convert_to_target(sel)
            target_type = type(sel)
            if target_type not in selection_type_options:
                raise err_types.NotSupportedError(
                    f"Insert operation does not support target selection type {target_type}."
                )
        else:
            raise err_types.NotSupportedError(f"Insert does not accept a selection of purpose {use}.")

        return sel

    @classmethod
    def apply(cls, form):
        target = selection.get(cls.name(), "target")
        sel_checkers.check_selection(target)

        number = form_helpers.extract(form, "insert-number", name="number")
        form_helpers.validate_nonempty(number, name="number")
        number = form_helpers.parse_int(number, name="number")

        modifications.apply_transaction(
            modifications.Transaction(
                modification_name="INSERT",
                input=modifications.InsertInput(target=target, number=number),
            )
        )

    @classmethod
    def render(cls):
        use_sel = selection.render(cls.name(), "target")
        return render_template(
                "partials/bulk_editor/insert.html",
                use_sel=use_sel,
        )
