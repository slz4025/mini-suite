from dataclasses import dataclass

import src.errors.types as err_types
import src.selector.types as sel_types
import src.sheet as sheet

from src.bulk_editor.modifications.modification import Modification


@dataclass
class Input:
    target: sel_types.ColIndex


class Sort(Modification):
    @classmethod
    def name(cls):
        return "SORT"

    @classmethod
    def apply(cls, input: Input):
        target = input.target

        index = None
        if isinstance(target, sel_types.ColIndex):
            index = target.value
        else:
            raise err_types.NotSupportedError(
                f"Selection type {type(target)} is not valid for sort."
            )
        assert index is not None

        ptr = sheet.data.get()
        order_col = cls._order(ptr[:, index])
        # sort rows
        sheet.data.set(ptr[order_col])

    # return array representing order of elements in L
    # where Nones are first, then numericals, then strings
    @classmethod
    def _order(cls, L):
        L_with_index = [(e, i) for i, e in enumerate(L)]
        nones = [(e, i) for e, i in L_with_index if e is None]
        numerical = sorted([
            (e, i) for e, i in L_with_index
            if isinstance(e, bool) or isinstance(e, int) or isinstance(e, float)
        ])
        strings = sorted([(e, i) for e, i in L_with_index if isinstance(e, str)])
        final = nones + numerical + strings
        order_by_index = [i for e, i in final]
        assert len(order_by_index) == len(L)
        return order_by_index
