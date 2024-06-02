from settings import Settings

import src.selector.types as sel_types


upperleft = None
nrows = None
ncols = None
mrows = None
mcols = None


def get_upperleft():
    return upperleft


def set_upperleft(_upperleft):
    global upperleft
    upperleft = _upperleft


def get_dimensions():
    return nrows, ncols


def set_dimensions(_nrows, _ncols):
    global nrows, ncols
    nrows = _nrows
    ncols = _ncols


def get_move_increments():
    return mrows, mcols


def set_move_increments(_mrows, _mcols):
    global mrows, mcols
    mrows = _mrows
    mcols = _mcols


def init():
    set_upperleft(sel_types.CellPosition(
        row_index=sel_types.RowIndex(0),
        col_index=sel_types.ColIndex(0),
    ))
    set_dimensions(Settings.DIM_PORT_ROWS, Settings.DIM_PORT_COLS)
    set_move_increments(Settings.MOVE_INCR_ROWS, Settings.MOVE_INCR_COLS)
