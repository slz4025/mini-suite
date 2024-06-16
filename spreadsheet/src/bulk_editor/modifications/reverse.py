from dataclasses import dataclass
import numpy as np

import src.sheet as sheet

from src.bulk_editor.modifications.modification import Modification


@dataclass
class Input:
    pass


class Reverse(Modification):
    @classmethod
    def name(cls):
        return "REVERSE"

    @classmethod
    def apply(cls, input: Input):
        ptr = sheet.data.get()
        # reverse rows
        sheet.data.set(np.flipud(ptr))
