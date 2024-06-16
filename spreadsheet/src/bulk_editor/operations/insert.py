from flask import render_template

import src.errors.types as err_types
import src.selector.modes as sel_modes
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
            # In multi-element selections, it is possible
            # for the start value(s) to be greater than the end value(s).
            # In single-element selections, the end value(s) is always
            # greater than the start value(s).
            target_mode = sel_modes.from_selection(sel)
            if isinstance(sel, sel_types.RowRange):
                if sel.end.value - sel.start.value == 1:
                    sel = sel_types.RowIndex(sel.start.value)
                else:
                    raise err_types.NotSupportedError(
                        f"Insert operation does not support target selection mode {target_mode.value}. "
                        "Select a single row instead."
                    )
            elif isinstance(sel, sel_types.ColRange):
                if sel.end.value - sel.start.value == 1:
                    sel = sel_types.ColIndex(sel.start.value)
                else:
                    raise err_types.NotSupportedError(
                        f"Insert operation does not support target selection mode {target_mode.value}. "
                        "Select a single column instead."
                    )

            selection_mode_options = [
                sel_types.Mode.ROW_INDEX,
                sel_types.Mode.COLUMN_INDEX,
            ]

            target_mode = sel_modes.from_selection(sel)
            if target_mode not in selection_mode_options:
                raise err_types.NotSupportedError(
                    f"Insert operation does not support target selection mode {target_mode.value}."
                )
        else:
            raise err_types.NotSupportedError(f"Insert does not accept a selection of purpose {use}.")

        return sel

    @classmethod
    def validate_and_parse(cls, form):
        target = selection.get(cls.name(), "target")
        sel_types.check_selection(target)

        number = form_helpers.extract(form, "insert-number", name="number")
        form_helpers.validate_nonempty(number, name="number")
        number = form_helpers.parse_int(number, name="number")

        modification = modifications.Transaction(
            modification_name="INSERT",
            input=modifications.InsertInput(target=target, number=number),
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
                "partials/bulk_editor/insert.html",
                use_sel=use_sel,
        )
