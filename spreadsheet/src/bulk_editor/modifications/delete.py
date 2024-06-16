from dataclasses import dataclass
import numpy as np

import src.errors.types as err_types
import src.selector.types as sel_types
import src.sheet as sheet

from src.bulk_editor.modifications.modification import Modification
from src.bulk_editor.modifications.types import Axis


@dataclass
class Input:
    selection: sel_types.RowRange | sel_types.ColRange


class Delete(Modification):
    @classmethod
    def name(cls):
        return "DELETE"

    @classmethod
    def apply(cls, input: Input):
        sel = input.selection

        start = None
        end = None
        axis = None

        if isinstance(sel, sel_types.RowRange):
            start = sel.start.value
            end = sel.end.value
            axis = Axis.ROW
        elif isinstance(sel, sel_types.ColRange):
            start = sel.start.value
            end = sel.end.value
            axis = Axis.COLUMN
        else:
            raise err_types.NotSupportedError(
                f"Selection type {type(sel)} is not valid for delete."
            )

        assert start is not None
        assert end is not None
        assert axis is not None

        ptr = sheet.data.get()
        indices = list(range(start, end))
        sheet.data.set(np.delete(ptr, indices, axis.value))
