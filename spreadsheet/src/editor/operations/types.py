from enum import Enum
from dataclasses import dataclass
from typing import Callable


class Name(Enum):
    TRUE = "true"
    FALSE = "false"
    MARKDOWN = "markdown"
    FORMULA = "formula"
    NEIGHBORS = "neighbors"
    SELECTION = "selection"


@dataclass
class Operation:
    name: Name
    template: Callable[[], str]
