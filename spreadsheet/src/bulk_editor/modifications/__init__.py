from dataclasses import dataclass
from typing import Any

from src.bulk_editor.modifications.insert import Insert, Input as InsertInput
from src.bulk_editor.modifications.delete import Delete, Input as DeleteInput
from src.bulk_editor.modifications.value import Value, Input as ValueInput
from src.bulk_editor.modifications.copy import Copy, Input as CopyInput
from src.bulk_editor.modifications.paste import Paste, Input as PasteInput
from src.bulk_editor.modifications.sort import Sort, Input as SortInput
from src.bulk_editor.modifications.reverse import Reverse, Input as ReverseInput


modifications = [
    Insert,
    Delete,
    Value,
    Copy,
    Paste,
    Sort,
    Reverse,
]
modifications_map = {m.name(): m for m in modifications}


@dataclass
class Transaction:
    modification_name: str
    input: Any


def apply_transaction(transaction):
    modification = modifications_map[transaction.modification_name]
    modification.apply(transaction.input)
