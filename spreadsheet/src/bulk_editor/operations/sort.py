from flask import render_template

import src.errors.types as err_types
import src.selector.modes as sel_modes
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
            selection_mode_options = [
                sel_types.Mode.COLUMN_INDEX,
            ]

            sel = selection.convert_to_target(sel)
            target_mode = sel_modes.from_selection(sel)
            if target_mode not in selection_mode_options:
                raise err_types.NotSupportedError(
                    f"Sort operation does not support target selection mode {target_mode.value}."
                )
        else:
            raise err_types.NotSupportedError(f"Sort does not accept a selection of purpose {use}.")

        return sel

    @classmethod
    def validate_and_parse(cls, form):
        target = selection.get(cls.name(), "target")
        sel_types.check_selection(target)

        modification = modifications.Transaction(
            modification_name="SORT",
            input=modifications.SortInput(target=target),
        )
        return [modification]

    @classmethod
    def apply(cls, mods):
        for modification in mods:
            modifications.apply_transaction(modification)

    @classmethod
    def render(cls):
        use_sel = selection.render(cls.name(), "target")
        return render_template(
                "partials/bulk_editor/sort.html",
                use_sel=use_sel,
        )
