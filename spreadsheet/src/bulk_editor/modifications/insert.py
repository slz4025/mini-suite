from dataclasses import dataclass
import numpy as np

import src.errors.types as err_types
import src.selector.types as sel_types
import src.sheet as sheet

from src.bulk_editor.modifications.modification import Modification
from src.bulk_editor.modifications.types import Axis


@dataclass
class Input:
    target: sel_types.RowIndex | sel_types.ColIndex
    number: int


class Insert(Modification):
    @classmethod
    def name(cls):
        return "INSERT"

    @classmethod
    def apply(cls, input: Input):
        target = input.target
        number = input.number

        index = None
        axis = None

        if isinstance(target, sel_types.RowIndex):
            index = target.value
            axis = Axis.ROW
        elif isinstance(target, sel_types.ColIndex):
            index = target.value
            axis = Axis.COLUMN
        else:
            raise err_types.NotSupportedError(
                f"Selection type, {type(target)}, is not valid for insert."
            )

        assert index is not None
        assert axis is not None

        ptr = sheet.data.get()
        insertion = np.array([[None] * number])
        sheet.data.set(np.insert(
            ptr,
            [index] * number,
            insertion if axis == Axis.COLUMN else insertion.T,
            axis=axis.value,
        ))
