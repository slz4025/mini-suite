from dataclasses import dataclass

import src.errors.types as err_types
import src.selector.types as sel_types
import src.sheet as sheet

from src.bulk_editor.modifications.modification import Modification
import src.bulk_editor.modifications.state as state


@dataclass
class Input:
    target: sel_types.RowIndex | sel_types.ColIndex | sel_types.CellPosition


class Paste(Modification):
    @classmethod
    def name(cls):
        return "PASTE"

    @classmethod
    def apply(cls, input: Input):
        target = input.target

        buf = state.get_buffer()
        if buf is None:
            raise err_types.UserError("Nothing in buffer to paste from.")

        if isinstance(target, sel_types.RowIndex):
            row_start = target.value
            row_end = row_start + buf.shape[0]
            col_start = 0
            col_end = buf.shape[1]
            assert col_end == sheet.data.get_bounds().col.value
        elif isinstance(target, sel_types.ColIndex):
            row_start = 0
            row_end = buf.shape[0]
            assert row_end == sheet.data.get_bounds().row.value
            col_start = target.value
            col_end = col_start + buf.shape[1]
        elif isinstance(target, sel_types.CellPosition):
            row_start = target.row_index.value
            row_end = row_start + buf.shape[0]
            col_start = target.col_index.value
            col_end = col_start + buf.shape[1]
        else:
            raise err_types.NotSupportedError(
                f"Selection type, {type(target)}, is not valid for paste."
            )

        ptr = sheet.data.get()
        ptr[row_start:row_end, col_start:col_end] = buf
