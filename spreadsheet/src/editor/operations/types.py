from enum import Enum
from dataclasses import dataclass
from typing import Callable


class Name(Enum):
    SUM = "Sum"
    AVERAGE = "Average"


@dataclass
class Operation:
    name: Name
    template: str
    render: Callable[[], str]
