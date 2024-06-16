from dataclasses import dataclass

import src.selector.types as sel_types
import src.sheet as sheet

from src.bulk_editor.modifications.modification import Modification


@dataclass
class Input:
    selection: sel_types.RowRange \
        | sel_types.ColRange \
        | sel_types.Box
    value: object


class Value(Modification):
    @classmethod
    def name(cls):
        return "VALUE"

    @classmethod
    def apply(cls, input: Input):
        sel = input.selection
        value = input.value

        row_start, row_end, col_start, col_end = \
            sel_types.get_bounds_from_selection(sel)

        ptr = sheet.data.get()
        ptr[row_start:row_end, col_start:col_end] = value
