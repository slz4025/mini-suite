from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional

import src.selector.types as sel_types

import src.bulk_editor.modifications as modifications


class Name(Enum):
    CUT = 'Cut'
    COPY = 'Copy'
    PASTE = 'Paste'
    DELETE = 'Delete'
    MOVE = 'Move'
    INSERT = 'Insert'
    ERASE = 'Erase'
    VALUE = 'Value'
    # The following are only shortcuts.
    MOVE_FORWARD = 'Move Forward'
    MOVE_BACKWARD = 'Move Backward'
    INSERT_END_ROWS = 'Insert End Rows'
    INSERT_END_COLS = 'Insert End Columns'


@dataclass
class Operation:
    name: Name
    icon: str
    validate_and_parse: Callable[[List[sel_types.Selection], object], List[modifications.Modification]]
    apply: Callable[[List[modifications.Modification]], None]
    render: Callable[[], str]
