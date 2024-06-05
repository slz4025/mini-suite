from enum import Enum
from dataclasses import dataclass


class Name(Enum):
    SUM = "Sum"
    AVERAGE = "Average"


@dataclass
class Operation:
    name: Name
    template: str
