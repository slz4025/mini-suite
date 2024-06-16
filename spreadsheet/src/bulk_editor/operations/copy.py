from flask import render_template

import src.errors.types as err_types
import src.selector.modes as sel_modes
import src.selector.types as sel_types

import src.bulk_editor.modifications as modifications
from src.bulk_editor.operations.operation import Operation
import src.bulk_editor.operations.selection as selection
import src.bulk_editor.operations.state as state


class Copy(Operation):
    @classmethod
    def name(cls):
        return "Copy"

    @classmethod
    def icon(cls):
        return "⧉"

    @classmethod
    def validate_selection(cls, use, sel):
        if use == "input":
            sel_mode = sel_modes.from_selection(sel)
            selection_mode_options = [
                sel_types.Mode.ROWS,
                sel_types.Mode.COLUMNS,
                sel_types.Mode.BOX,
            ]
            if sel_mode not in selection_mode_options:
                raise err_types.NotSupportedError(
                    f"Copy operation does not support selection mode {sel_mode.value}."
                )
        else:
            raise err_types.NotSupportedError(f"Copy does not accept a selection of purpose {use}.")

        return sel

    @classmethod
    def apply(cls, form):
        sel = selection.get(cls.name(), "input")
        sel_types.check_selection(sel)
        state.set_buffer_mode(sel)

        modifications.apply_transaction(
            modifications.Transaction(
                modification_name="COPY",
                input=modifications.CopyInput(selection=sel),
            )
        )

    @classmethod
    def render(cls):
        use_sel = selection.render(cls.name(), "input")
        return render_template(
                "partials/bulk_editor/copy.html",
                use_sel=use_sel,
        )
