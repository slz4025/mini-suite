from flask import render_template

import src.errors.types as err_types
import src.selector.modes as sel_modes
import src.selector.state as sel_state
import src.selector.types as sel_types
import src.sheet.types as sheet_types

import src.bulk_editor.modifications as modifications
from src.bulk_editor.operations.operation import Operation
import src.bulk_editor.operations.selection as selection


class Move(Operation):
    @classmethod
    def name(cls):
        return "Move"

    @classmethod
    def icon(cls):
        return "❖"

    @classmethod
    def validate_selection(cls, use, sel):
        if use == "input":
            sel_mode = sel_modes.from_selection(sel)
            if isinstance(sel, sel_types.RowRange):
                pass
            elif isinstance(sel, sel_types.ColRange):
                pass
            else:
                raise err_types.NotSupportedError(
                    f"Move operation does not support input selection mode {sel_mode.value}."
                )
        elif use == "target":
            # requires input selection to be inputted first
            input_sel = selection.get(cls.name(), "input")
            sel_mode = sel_modes.from_selection(input_sel)

            sel = selection.convert_to_target(sel)
            target_mode = sel_modes.from_selection(sel)
            if isinstance(input_sel, sel_types.RowRange):
                if not isinstance(sel, sel_types.RowIndex):
                    raise err_types.NotSupportedError(
                        f"Move operation does not support target selection mode {target_mode.value} for input selection mode {sel_mode.value}."
                    )
            elif isinstance(input_sel, sel_types.ColRange):
                if not isinstance(sel, sel_types.ColIndex):
                    raise err_types.NotSupportedError(
                        f"Move operation does not support target selection mode {target_mode.value} for input selection mode {sel_mode.value}."
                    )
        else:
            raise err_types.NotSupportedError(f"Move does not accept a selection of purpose {use}.")

        return sel

    @classmethod
    def validate_and_parse(cls, form):
        sel = selection.get(cls.name(), "input")
        sel_types.check_selection(sel)
        target = selection.get(cls.name(), "target")
        sel_types.check_selection(target)

        num = None
        adjusted_target = None
        if isinstance(sel, sel_types.RowRange):
            assert isinstance(target, sel_types.RowIndex)

            num = sel.end.value - sel.start.value
            curr_pos = target.value
            if curr_pos < sel.start.value:
                adjusted_target = target
            elif curr_pos > sel.end.value:
                adjusted_target = sel_types.RowIndex(curr_pos - num)
            else:
                raise err_types.UserError(
                    "Cannot move input selection to a target selection within original bounds."
                )
        elif isinstance(sel, sel_types.ColRange):
            assert isinstance(target, sel_types.ColIndex)

            num = sel.end.value - sel.start.value
            curr_pos = target.value
            if curr_pos < sel.start.value:
                adjusted_target = target
            elif curr_pos > sel.end.value:
                adjusted_target = sel_types.ColIndex(curr_pos - num)
            else:
                raise err_types.UserError(
                    "Cannot move input selection to a target selection within original bounds."
                )
        assert num is not None
        assert adjusted_target is not None

        mods = [
            modifications.Transaction(
                modification_name="COPY",
                input=modifications.CopyInput(selection=sel),
            ),
            modifications.Transaction(
                modification_name="DELETE",
                input=modifications.DeleteInput(selection=sel),
            ),
            modifications.Transaction(
                modification_name="INSERT",
                input=modifications.InsertInput(target=adjusted_target, number=num),
            ),
            modifications.Transaction(
                modification_name="PASTE",
                input=modifications.PasteInput(target=adjusted_target),
            ),
        ]
        return mods

    @classmethod
    def apply(cls, mods):
        for modification in mods:
            modifications.apply_transaction(modification)

        # update selection to wherever cells ended up
        copy_mod = mods[0]
        assert copy_mod.modification_name == "COPY"
        sel = copy_mod.input.selection

        paste_mod = mods[-1]
        assert paste_mod.modification_name == "PASTE"
        target = paste_mod.input.target

        new_start = target.value
        if isinstance(sel, sel_types.RowRange):
            num = sel.end.value - sel.start.value
            new_sel = sel_types.RowRange(
                start=sheet_types.Index(new_start),
                end=sheet_types.Bound(new_start + num),
            )
            sel_state.set_selection(new_sel)
        elif isinstance(sel, sel_types.ColRange):
            num = sel.end.value - sel.start.value
            new_sel = sel_types.ColRange(
                start=sheet_types.Index(new_start),
                end=sheet_types.Bound(new_start + num),
            )
            sel_state.set_selection(new_sel)

    @classmethod
    def render(cls):
        use_sel_input = selection.render(cls.name(), "input")
        use_sel_target = selection.render(cls.name(), "target")
        return render_template(
                "partials/bulk_editor/move.html",
                use_sel_input=use_sel_input,
                use_sel_target=use_sel_target,
        )
