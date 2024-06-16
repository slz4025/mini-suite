from dataclasses import dataclass

import src.selector.types as sel_types
import src.sheet as sheet

from src.bulk_editor.modifications.modification import Modification
import src.bulk_editor.modifications.state as state


@dataclass
class Input:
    selection: sel_types.RowRange | sel_types.ColRange | sel_types.Box


class Copy(Modification):
    @classmethod
    def name(cls):
        return "COPY"

    @classmethod
    def apply(cls, input: Input):
        sel = input.selection

        row_start, row_end, col_start, col_end = \
            sel_types.get_bounds_from_selection(sel)

        ptr = sheet.data.get()
        buf = ptr[row_start:row_end, col_start:col_end]
        state.set_buffer(buf)
