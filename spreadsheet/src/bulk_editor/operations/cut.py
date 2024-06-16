from flask import render_template

import src.errors.types as err_types
import src.selector.modes as sel_modes
import src.selector.types as sel_types

import src.bulk_editor.modifications as modifications
from src.bulk_editor.operations.operation import Operation
import src.bulk_editor.operations.selection as selection
import src.bulk_editor.operations.state as state


class Cut(Operation):
    @classmethod
    def name(cls):
        return "Cut"

    @classmethod
    def icon(cls):
        return "✂"

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
                    f"Cut operation does not support selection mode {sel_mode.value}."
                )
        else:
            raise err_types.NotSupportedError(f"Cut does not accept a selection of purpose {use}.")

        return sel

    @classmethod
    def validate_and_parse(cls, form):
        sel = selection.get(cls.name(), "input")
        sel_types.check_selection(sel)

        mods = []

        modification = modifications.Transaction(
            modification_name="COPY",
            input=modifications.CopyInput(selection=sel),
        )
        mods.append(modification)

        modification = modifications.Transaction(
            modification_name="VALUE",
            input=modifications.ValueInput(selection=sel, value=None),
        )
        mods.append(modification)

        return mods

    @classmethod
    def apply(cls, mods):
        assert len(mods) == 2
        copy_mod = mods[0]
        assert copy_mod.modification_name == "COPY"
        sel = copy_mod.input.selection

        state.set_buffer_mode(sel)
        for modification in mods:
            modifications.apply_transaction(modification)

    @classmethod
    def render(cls):
        use_sel = selection.render(cls.name(), "input")
        return render_template(
                "partials/bulk_editor/cut.html",
                use_sel=use_sel,
        )
