from dataclasses import dataclass
import json
import numpy as np
from typing import Optional


sheet = None


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


def get_bounds():
    shape = sheet.shape
    return Bounds(row=Bound(shape[0]), col=Bound(shape[1]))


def init(debug=False):
    global sheet

    maxrows = 10
    maxcols = 10

    sheet = np.empty((maxrows, maxcols), dtype=object)
    if debug:
        for row in range(maxrows):
            for col in range(maxcols):
                sheet[row, col] = row*maxcols + col


def get():
    return sheet


def get_cell_value(cell_position):
    return sheet[cell_position.row_index.value, cell_position.col_index.value]


def set(data):
    global sheet

    sheet = data


def get_dump():
    data = []
    for row in range(sheet.shape[0]):
        data.append(sheet[row].tolist())
    return json.dumps(data)
