from dataclasses import dataclass
import json
import numpy as np
from typing import Optional


sheet = None


@dataclass
class Index:
    value: int


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

    maxrows = 100
    maxcols = 100

    sheet = np.empty((maxrows, maxcols), dtype=object)
    if debug:
        for row in range(maxrows):
            for col in range(maxcols):
                sheet[row, col] = f"{row}x{col}"


def get():
    return sheet


def set(data):
    global sheet

    sheet = data


def get_dump():
    data = []
    for row in range(sheet.shape[0]):
        data.append(sheet[row].tolist())
    return json.dumps(data)
