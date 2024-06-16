from flask import render_template

import src.errors.types as err_types
import src.selector.modes as sel_modes
import src.selector.types as sel_types

import src.bulk_editor.modifications as modifications
from src.bulk_editor.operations.operation import Operation
import src.bulk_editor.operations.selection as selection
import src.bulk_editor.operations.state as state


class Paste(Operation):
    @classmethod
    def name(cls):
        return "Paste"

    @classmethod
    def icon(cls):
        return "📋"

    @classmethod
    def validate_selection(cls, use, sel):
        if use == "target":
            copy_to_paste = {
                sel_types.Mode.ROWS: sel_types.Mode.ROW_INDEX,
                sel_types.Mode.COLUMNS: sel_types.Mode.COLUMN_INDEX,
                sel_types.Mode.BOX: sel_types.Mode.CELL_POSITION,
            }
            copy_selection_mode = state.get_buffer_mode()

            selection_mode_options = []
            if copy_selection_mode is None:
                raise err_types.UserError("Paste operation has nothing to copy.")
            elif copy_selection_mode not in copy_to_paste:
                raise err_types.NotSupportedError(
                    f"Paste operation does not support buffer selection type {copy_selection_mode.value}."
                )
            else:
                selection_mode_options = [copy_to_paste[copy_selection_mode]]

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
                        f"Paste operation does not support target selection mode {target_mode.value}. "
                        "Select a single row instead."
                    )
            elif isinstance(sel, sel_types.ColRange):
                if sel.end.value - sel.start.value == 1:
                    sel = sel_types.ColIndex(sel.start.value)
                else:
                    raise err_types.NotSupportedError(
                        f"Paste operation does not support target selection mode {target_mode.value}. "
                        "Select a single column instead."
                    )
            elif isinstance(sel, sel_types.Box):
                if sel.row_range.end.value - sel.row_range.start.value == 1 \
                        and sel.col_range.end.value - sel.col_range.start.value == 1:
                    sel = sel_types.CellPosition(
                        row_index=sel_types.RowIndex(sel.row_range.start.value),
                        col_index=sel_types.ColIndex(sel.col_range.start.value),
                    )
                else:
                    raise err_types.NotSupportedError(
                        f"Paste operation does not support target selection mode {target_mode.value}. "
                        "Select a single cell instead."
                    )

            target_mode = sel_modes.from_selection(sel)
            if target_mode not in selection_mode_options:
                raise err_types.NotSupportedError(
                    f"Paste operation does not support target selection mode {target_mode.value} "
                    f"for copied buffer type {copy_selection_mode.value}."
                )
        else:
            raise err_types.NotSupportedError(f"Paste does not accept a selection of purpose {use}.")

        return sel

    @classmethod
    def validate_and_parse(cls, form):
        target = selection.get(cls.name(), "target")
        sel_types.check_selection(target)

        modification = modifications.Transaction(
            modification_name="PASTE",
            input=modifications.PasteInput(target=target),
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
                "partials/bulk_editor/paste.html",
                use_sel=use_sel,
        )
