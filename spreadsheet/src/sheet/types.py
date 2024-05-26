from dataclasses import dataclass
from typing import Optional


class Index:
    def __init__(self, value):
        self.value = value

    def equals(self, other):
        return self.value == other.value

    # end-exclusive
    def in_bounds(self, start, end):
        return self.value >= start and self.value < end


@dataclass
class Bound:
    value: int


DynamicIndex = Optional[Index]
DynamicBound = Optional[Bound]


@dataclass
class Range:
    start: DynamicIndex
    end: DynamicBound


@dataclass
class Bounds:
    # just ending index
    row: Bound
    col: Bound
