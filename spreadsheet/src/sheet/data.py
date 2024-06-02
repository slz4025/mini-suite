import numpy as np

from settings import Settings

import src.sheet.types as types


sheet = None


def get_bounds():
    shape = sheet.shape
    return types.Bounds(row=types.Bound(shape[0]), col=types.Bound(shape[1]))


def get():
    return sheet


def set(data):
    global sheet
    sheet = data


def get_cell_value(cell_position):
    return sheet[cell_position.row_index.value, cell_position.col_index.value]


def init(debug=False):
    global sheet

    maxrows = Settings.DIM_SHEET_ROWS
    maxcols = Settings.DIM_SHEET_COLS

    sheet = np.empty((maxrows, maxcols), dtype=object)
    if debug:
        for row in range(maxrows):
            for col in range(maxcols):
                sheet[row, col] = row*maxcols + col
