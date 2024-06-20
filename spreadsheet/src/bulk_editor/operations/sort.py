from flask import render_template

import src.errors.types as err_types
import src.selector.checkers as sel_checkers
import src.selector.types as sel_types

import src.bulk_editor.modifications as modifications
from src.bulk_editor.operations.operation import Operation
import src.bulk_editor.operations.selection as selection


class Sort(Operation):
    @classmethod
    def name(cls):
        return "Sort"

    @classmethod
    def icon(cls):
        return ""

    @classmethod
    def validate_selection(cls, use, sel):
        if use == "target":
            selection_type_options = [
                sel_types.ColIndex,
            ]

            sel = selection.convert_to_target(sel)
            target_type = type(sel)
            if target_type not in selection_type_options:
                raise err_types.NotSupportedError(
                    f"Sort operation does not support target selection type {target_type}."
                )
        else:
            raise err_types.NotSupportedError(f"Sort does not accept a selection of purpose {use}.")

        return sel

    @classmethod
    def apply(cls, form):
        target = selection.get(cls.name(), "target")
        sel_checkers.check_selection(target)

        modifications.apply_transaction(
            modifications.Transaction(
                modification_name="SORT",
                input=modifications.SortInput(target=target),
            )
        )

    @classmethod
    def render(cls):
        use_sel = selection.render(cls.name(), "target")
        return render_template(
                "partials/bulk_editor/sort.html",
                use_sel=use_sel,
        )
