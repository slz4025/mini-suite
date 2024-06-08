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
    INSERT = 'Insert'
    INSERT_END_ROWS = 'Insert End Rows'
    INSERT_END_COLS = 'Insert End Columns'
    ERASE = 'Erase'
    VALUE = 'Value'


@dataclass
class Operation:
    name: Name
    icon: str
    validate_and_parse: Callable[[List[sel_types.Selection], object], List[modifications.Modification]]
    apply: Callable[[List[modifications.Modification]], None]
    render: Callable[[], str]
